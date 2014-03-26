import mimetypes
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_file_type(value):
    mimetype = mimetypes.guess_type(value.name)[0]

    if value.size > settings.MAX_FILE_SIZE:
        raise ValidationError(_('File too large'))

    if not mimetype or not any(mimetype.startswith(x) for x in settings.ALLOWED_FILE_TYPES):
        raise ValidationError(_('File type not allowed'))
