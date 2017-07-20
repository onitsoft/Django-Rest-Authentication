from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'),
    }
}

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'hellgy'
EMAIL_HOST_PASSWORD = '123q123q'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
