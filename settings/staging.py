from base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vita',
        'USER': 'vita',
        'HOST': 'vitastaging.cww4gfvmqeyv.us-east-1.rds.amazonaws.com',
        'PASSWORD': '1777c232bc6bd9ec38f',
        'PORT': '3306',
    }
}

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'hellgy'
EMAIL_HOST_PASSWORD = '123q123q'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
