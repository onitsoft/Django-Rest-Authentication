from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from models import User


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.

    Needed to override the default to get rid of the "username" field
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'change_password', )}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone',
                                         'location', 'status', 'image', )}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'last_activity',
                                           'created', 'modified', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )
    readonly_fields = ('created', 'modified', 'last_login', 'change_password',
                       'last_activity', )
    exclude = ('password', )

    form = forms.ModelForm
    add_form = UserCreationForm

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'status', )
    list_filter = ('is_staff', 'is_superuser', 'groups', 'status', )
    ordering = ('email', )
    search_fields = ('first_name', 'last_name', 'email')
    actions = ('close_user_account', )

    def change_password(self, obj):
        return '<a href="password/">Change password</a>'
    change_password.allow_tags = True

    def close_user_account(self, request, queryset):
        """Custom admin action for closing user accounts"""
        queryset.update(status=User.Status.CLOSED)

admin.site.register(User, UserAdmin)
