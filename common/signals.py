from django.conf import settings
from django.db.models.signals import post_save
from easy_thumbnails.alias import aliases
from profiles import User

DEFAULT_THUMBNAIL_ALIAS = '100'


def has_thumbnail(imagefield):
    """Check if an image field already has a default thumbnail"""
    return bool(imagefield.get_thumbnail(aliases.get(DEFAULT_THUMBNAIL_ALIAS), generate=False))


def generate_image_thumbnails(sender, instance, created, **kwargs):
    if not instance.image or has_thumbnail(instance.image) or not settings.THUMBNAILS_ENABLED:
        return

    from tasks import generate_thumbnails
    generate_thumbnails.delay(sender, instance.pk, 'image')


for model in [User]:
    post_save.connect(generate_image_thumbnails, sender=model,
                      dispatch_uid='common.signals')
