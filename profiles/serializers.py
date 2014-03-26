from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from common.fields import ImageURLField, CroppedImageURLField
from common.serializers import CustomSerializer, CustomModelSerializer


from .models import User, PasswordResetRequest


def validate_password(password):
    if password and len(password) < settings.MIN_PASSWORD_LENGTH:
        raise ValidationError(_('The password should be at least {length} characters long.')
                              .format(length=settings.MIN_PASSWORD_LENGTH))
    return True


class NestedSocialCredentialsSerializer(CustomModelSerializer):
    class Meta:
        pass
        # model = SocialCredentials
        # fields = ('media_type', 'media_user_id')


class UserSerializer(CustomModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name',
                  'phone',
                  'last_ip', 'registration_ip',
                  'password', 'show_welcome_dialog',
                  'image', 'image_crop_mini', 'image_crop_100')

        read_only_fields = ('is_staff', 'last_ip',
                            'registration_ip',)

    password = serializers.CharField(
        label=_('Password'),
        help_text='Set the password, leave empty to keep the previous password',
        required=False
    )

    image = ImageURLField(required=False)
    image_crop_100 = CroppedImageURLField(source='image', thumbnail_alias='100')
    image_crop_mini = CroppedImageURLField(source='image', thumbnail_alias='mini')

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        import ipdb; ipdb.set_trace()
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        if 'view' in self.context and self.context['view'].action == 'create':
            # password is required only on creation
            self.fields['password'].required = True

    def get_fields(self):
        """
        Only the accessing user can view his permissions and connected media.
        """
        fields = super(UserSerializer, self).get_fields()

        if 'view' not in self.context or not self.context['request'].user == self.object:
            fields.pop('profiles', None)
            fields.pop('show_welcome_dialog', None)
            fields.pop('last_ip', None)
            fields.pop('registration_ip', None)

    def to_native(self, obj):
        native = super(UserSerializer, self).to_native(obj)

        native.pop('password', None)  # Remove password field when serializing an object

        return native

    def restore_object(self, attrs, instance=None):
        password = attrs.pop('password', '')
        self.fields.pop('password', None)  # hack to avoid validation errors

        obj = super(UserSerializer, self).restore_object(attrs, instance)

        if not obj.pk:
            # Set ips on user creation
            if 'request' in self.context:
                obj.registration_ip = self.context['request'].META['REMOTE_ADDR']
                obj.last_ip = self.context['request'].META['REMOTE_ADDR']

        obj.email = obj.email.lower()  # make the email lowercase!

        if password:
            obj.set_password(password)  # Set password if it has been set / changed

        return obj

    def validate_password(self, attrs, source):
        validate_password(attrs.get(source, None))
        return attrs


class UserDetailsSerializer(CustomModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', )
        read_only_fields = fields


class UserPhotosSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'image_crop_mini', 'current')

    current = serializers.SerializerMethodField('is_current_user')

    def is_current_user(self, obj):
        user = (self.context.get('current_user') or
                getattr(self.context.get('request'), 'user', None))
        return obj == user


class AuthenticationSerializer(CustomSerializer):
    """
    Seralizer version of django.contrib.auth.forms.AuthenticationForm
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = (attrs.get('email') or '').lower()

        self.user = authenticate(username=email,
                                 password=attrs['password'])

        if not self.user:
            raise ValidationError(_('Invalid E-mail or password.'))

        return attrs


class PasswordResetSerializer(CustomSerializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, attrs, source):
        email = attrs.get(source)

        if email:
            try:
                user = User.objects.get(email=email)
                self._user = user  # Cache for using in view later
            except User.DoesNotExist:
                raise ValidationError(_('Invalid E-mail. No such user.'))


class PasswordResetCompleteSerializer(CustomSerializer):
    hash = serializers.CharField(required=True, help_text=_('Password reset hash'))
    password = serializers.CharField(required=True, help_text=_('The new password'))

    def validate_hash(self, attrs, source):
        hash_ = attrs.get(source, '')
        try:
            prp = PasswordResetRequest.objects.get(hash=hash_)
            self._user = prp.user  # Cache for using in view later
        except PasswordResetRequest.DoesNotExist:
            raise ValidationError(_('Invalid password reset hash'))

        return attrs

    def validate_password(self, attrs, source):
        validate_password(attrs.get(source, None))
        return attrs
