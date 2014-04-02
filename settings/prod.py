from base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vita_auth',
        'USER': 'vita_auth',
        'HOST': 'db1.cww4gfvmqeyv.us-east-1.rds.amazonaws.com',
        'PASSWORD': 'cfa5157a22b3f6184',
        'PORT': '3306',
    }
}

DEBUG = False
TEMPLATE_DEBUG = DEBUG
