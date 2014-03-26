import hashlib
import uuid
import string
import random
from django.conf import settings


def get_image_upload_path(instance, filename):
    # filename is uuid + the orinal extension
    return 'images/{filename}.{ext}'.format(filename=uuid.uuid4().hex,
                                            ext=filename.split('.')[-1])


def get_external_url(obj, class_name=None):
    class_name = class_name or obj.__class__.__name__

    try:
        url = settings.EXTERNAL_URLS[class_name]
    except KeyError:
        raise ValueError('Unsupported object type')

    return url.format(obj=obj, scheme=settings.EXTERNAL_SITE_SCHEME,
                      domain=settings.EXTERNAL_SITE_DOMAIN)


def generate_secure_hash():
    """
    Returns a unique SHA hash
    """
    return hashlib.sha1(uuid.uuid4().bytes).hexdigest()


def generate_random_string(length):
    return ''.join([random.choice(string.letters + string.digits)
                    for i in range(length)])
