import base64
import logging

from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.alias import aliases
from rest_framework import serializers


logger = logging.getLogger('vita_auth.common.fields')


class Base64ImageField(serializers.ImageField):
    #Field for persoanl awatar
    def from_native(self, data):
        if isinstance(data, basestring) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super(Base64ImageField, self).from_native(data)


class ImageURLField(Base64ImageField):
    def get_absoulute_url(self, url):
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else ''

    def to_native(self, value):
        return self.get_absoulute_url(value.url) if value else ''


class CroppedImageURLField(ImageURLField):
    def __init__(self, *args, **kwargs):
        self.thumbnail_alias = kwargs.pop('thumbnail_alias')
        self.force_generate = kwargs.pop('force_generate', False)

        kwargs['read_only'] = True
        super(CroppedImageURLField, self).__init__(*args, **kwargs)

    def to_native(self, value):
        if value:
            try:
                thumb = value.get_thumbnail(aliases.get(self.thumbnail_alias),
                                            generate=self.force_generate)

                url = thumb.url if thumb else value.url
                return self.get_absoulute_url(url)
            except Exception:  # pragma: nocover
                logger.exception('Error getting image thumbnail')

        return super(CroppedImageURLField, self).to_native(value)


class OptionalFileField(serializers.FileField):
    def to_native(self, value):
        return value.name if value else None


class EmailListField(serializers.EmailField):
    default_error_messages = {
        'invalid': _('Invalid E-mail address.'),
    }

    def from_native(self, value):
        return [super(EmailListField, self).from_native(email) for email in value]

    def validate(self, value):
        if not isinstance(value, list) or not value:
            raise ValidationError(_('List of e-mails required!'))

        for email in value:
            if not email or not isinstance(email, basestring):
                raise ValidationError(self.default_error_messages['invalid'])

    def run_validators(self, value):
        for email in value:
            super(EmailListField, self).run_validators(email)
