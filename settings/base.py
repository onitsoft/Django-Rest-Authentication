"""
Django settings for vita_auth project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

# Absolute project path (for convinience)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, '..')


DEBUG = True
TEMPLATE_DEBUG = DEBUG


ADMINS = (
    ('Oleg', 'hellgy@gmail.com'),
)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fz%4rpd=u0m-813=a%itl)48i11asdd!bsgiw#w@_($kiuigf(++py'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

#for the chrome extension
ALLOWED_HOSTS = ('*')

gettext = lambda x: x
LANGUAGES = (
    ('en', gettext('English')),
    ('he', gettext('Hebrew')),
)

# Application definition
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'easy_thumbnails',
    'rest_framework',
    'south',
    'corsheaders',
    'profiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    # 'useful.context_processors.settings',
)
ROOT_URLCONF = 'vita_auth.urls'

WSGI_APPLICATION = 'vita_auth.wsgi.application'

GEOIP_PATH = os.path.join(PROJECT_ROOT, 'GeoIP.dat')

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases


ROOT_URLCONF = 'vita_auth.urls'

WSGI_APPLICATION = 'wsgi.application'
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

AUTH_USER_MODEL = 'profiles.User'

MIN_PASSWORD_LENGTH = 4


SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week (in seconds)
SESSION_SAVE_EVERY_REQUEST = True

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(name)s : %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 20 * 1024 * 1024,  # 20MB
            'backupCount': 5,
            'filename': os.path.join(PROJECT_ROOT, 'logs', 'debug.log'),
            'formatter': 'default',
        },
        'error_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 20 * 1024 * 1024,  # 20MB
            'backupCount': 5,
            'filename': os.path.join(PROJECT_ROOT, 'logs', 'error.log'),
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file', 'error_file', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}


# Application settings

INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    # 'debug_toolbar.panels.logger.LoggingPanel',
)


CACHES = {
    "default": {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379:1",
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
        }
    }
}

PATCH_SETTINGS = True  # Let django-debug-toolbar to patch settings if it's enabled.


#For the hrome extensions
CORS_ORIGIN_ALLOW_ALL = False
# CORS_ORIGIN_WHITELIST = ("*")
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_REGEX_WHITELIST = ('^chrome-extension://*')
CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'cache-control',
    'Pragma',
    'authorization',
    'X-CSRFToken',

)
# CORS_ORIGIN_REGEX_WHITELIST = ()


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.OAuth2Authentication',#mobile clients
        'authentication.SessionAuthenticationNoCSRF',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',
                                'rest_framework.filters.OrderingFilter')
}
