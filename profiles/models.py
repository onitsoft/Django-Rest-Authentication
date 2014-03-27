from django.db import models
# from django_countries import CountryField

import logging
import pygeoip
import pytz
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from easy_thumbnails.fields import ThumbnailerImageField
from timezone_field import TimeZoneField
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
# from django_countries import CountryField

from common.utils import generate_secure_hash, get_image_upload_path, get_external_url

logger = logging.getLogger('tomigo.users.models')


# class Location(models.Model):
#     name = models.CharField(_('Name'), max_length=26, blank=False)
#     country = CountryField(blank=True)
#     city = models.CharField(_('City'), max_length=100, blank=True)
#     address = models.CharField(_('Address'), max_length=250, blank=True)

#     is_active = models.BooleanField(default=True)

#     def __unicode__(self):
#         return self.name or unicode(self.country.name)
# logger = logging.getLogger('vita_auth.profile.models')


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email.
        """
        user = self.model(email=UserManager.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)
        user.is_staff = False
        user.is_superuser = False

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, password=password)

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    """
    Modified version of AbstractBaseUser
    """

    email = models.EmailField(_('E-mail'), blank=False, null=False, unique=True)

    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'))

    is_superuser = models.BooleanField(
        _('Admin'), default=False,
        help_text=_('Designates whether the user is an admin - has all permissions'))
    first_name = models.CharField(_('First name'), max_length=30, blank=True)
    last_name = models.CharField(_('Last name'), max_length=30, blank=True)
    phone = models.CharField(_('Phone number'), max_length=16, blank=True)
    # location = models.ForeignKey(Location, verbose_name=_('Location'),
                                 # blank=True, null=True)

    registration_ip = models.IPAddressField(blank=True, null=True)
    last_ip = models.IPAddressField(blank=True, null=True)

    last_activity = models.DateTimeField(null=True, blank=True)

    timezone = TimeZoneField(null=True)

    image = ThumbnailerImageField(upload_to=get_image_upload_path, blank=True, null=True,
                                  verbose_name=_('Profile image'))

    show_welcome_dialog = models.BooleanField(default=True, verbose_name=_('Show welcome dialog?'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    # def is_superuser(self):
    #     return super()


    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return u'{0.first_name} {0.last_name}'.format(self).strip() or self.email

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name.strip() or self.email

    def update_from_request(self, request):
        """
        Update last activity and ip addresses.
        """

        if hasattr(self, 'updated'):
            return  # Avoid updating twice

        self.last_activity = timezone.now()
        update_fields = ['last_activity']  # premature optimization

        if self.last_ip != request.META['REMOTE_ADDR']:
            self.last_ip = request.META['REMOTE_ADDR']
            update_fields.append('last_ip')

        if not self.registration_ip:
            self.registration_ip = self.last_ip

            self.set_country_by_ip()
            self.set_timezone_by_country()

            update_fields.extend(['registration_ip', 'timezone'])

        self.updated = True
        self.save(update_fields=update_fields)

    def set_country_by_ip(self):
        geoip = pygeoip.GeoIP(settings.GEOIP_PATH)
        country = geoip.country_code_by_addr(self.registration_ip)
        logger.info('set_country_by_ip(): country: %s', country)

        # if country:
        #     self.location.country = country
        #     self.location.save()

    def set_timezone_by_country(self):
        """
        Try guessing the user's timezone by location.country
        """

        # try:
        #     self.timezone = pytz.country_timezones[self.location.country.code][0]
        # except (AttributeError, KeyError, IndexError):
        #     pass
    def has_perm(self, perm, obj=None):
      return self.is_staff

    def has_module_perms(self, app_label):
      return self.is_staff

class MedicalProfile(TimeStampedModel):
    class Age:
        YOUNGSTER = 27
        ADULT = 43
        ELDER = 60

        CHOICES = (
            (YOUNGSTER, YOUNGSTER),
            (ADULT, ADULT),
            (ELDER, ELDER)
        )

    class CoffeCups:
        ONE = 1
        TWO = 2
        THREE = 3

        CHOICES = (
            (ONE, _('One')),
            (TWO, _('Two')),
            (THREE, _('Three')),
        )

    class SkinMelanin:
        PALE = 1
        FAIR = 2
        WHITE = 3
        LIGHT_BROWN = 4
        BROWN = 5
        DARK_BROWN = 6

        CHOICES = (
            (PALE, 'Pale'),
            (FAIR, 'Fair'),
            (WHITE, 'White'),
            (LIGHT_BROWN, 'Light brown'),
            (BROWN, 'Brown'),
            (DARK_BROWN, 'Dark brown')
        )

    user = models.ForeignKey('profiles.User', blank=False)
    name = models.CharField(max_length=25, blank=True, null=True,
                            verbose_name=_("profile name"))
    age = models.IntegerField(max_length=3, blank=True, null=True,
                              choices=Age.CHOICES, verbose_name=_('age'))
    average_us_nutrition = models.BooleanField(blank=True,
                                               verbose_name=_('nutrition'))
    coffee_cups = models.IntegerField(blank=True, null=True,
                                      choices=CoffeCups.CHOICES,
                                      verbose_name=_('coffe cups'))
    contraceptives = models.BooleanField(blank=True,
                                         verbose_name=_('on the pill'))
    fluoride_enrich = models.BooleanField(blank=True)
    health_goals = models.BooleanField(blank=True,
                                       verbose_name=_('health goals'))
    health_goals_text = models.CharField(max_length=255,
                                         blank=True,
                                         verbose_name=_('health goals text'))
    lactation = models.BooleanField(blank=True,
                                    verbose_name=_('nursing'))
    low_sodium_diet = models.BooleanField(blank=True,
                                          verbose_name=_('low sodium diet'))
    malabsorption = models.BooleanField(blank=True,
                                        verbose_name=_('malabsorption'))
    male = models.BooleanField(blank=True, verbose_name=_('male'))
    medicines_text = models.CharField(max_length=150, blank=True,
                                      verbose_name=_('regularly consumed medecies'))
    medicines = models.BooleanField(blank=True,
                                    verbose_name=_('using medicines'))
    melanin = models.IntegerField(blank=True, null=True, max_length=2,
                                  choices=SkinMelanin.CHOICES)
    pregnancy = models.BooleanField(blank=True, verbose_name=_('pregnancy'))
    rda = models.BooleanField(blank=True, verbose_name=_('recommended daily allowance(FDA)'))
    smoker = models.BooleanField(blank=True, verbose_name=_('smoker)'))
    sunlight = models.BooleanField(blank=True, verbose_name=_('hihg sunlight exposure'))
    vegetarian = models.BooleanField(blank=True, verbose_name=_('vegeterian'))
    birthday = models.DateTimeField(blank=True, null=True, verbose_name=_('birthday'))

    class Meta:
        verbose_name = _('Medical profile')
        verbose_name_plural = _('Medical profiles')
        def __unicode__(self):
            return ("{profile}: {name}").format(profile=_("profile"),
                                                name=self.name)



class PasswordResetRequest(TimeStampedModel):
    user = models.OneToOneField(User)
    hash = models.CharField(max_length=40, default=generate_secure_hash)

    def external_url(self):
        return get_external_url(self)
