from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class PartialModelSerializer(serializers.ModelSerializer):
    """Like ModelSerializers - but accepts partial updates with PUT"""

    def __init__(self, *args, **kwargs):
        # kwargs['partial'] = True
        super(PartialModelSerializer, self).__init__(*args, **kwargs)

        request = self.context.get('request')

        if request and request.method == 'PUT' and self.object:
            self.partial = True


class FormatErrorsSerializer(serializers.Serializer):
    @property
    def errors(self):
        errors = super(FormatErrorsSerializer, self).errors
        if not errors:
            # Noting to do in this case, return as-is to that
            # is_valid still returns true.
            return {}

        formatted_errors = []
        non_field_errors = errors.get('non_field_errors', [])

        # Move __all__ errors to non_field_errors
        non_field_errors.extend(errors.pop('__all__', []))

        if non_field_errors:
            errors['non_field_errors'] = non_field_errors

        # Add non_field_errors on top
        formatted_errors.extend(non_field_errors)

        # Add formatted field errors
        for field_name, error_messages in errors.items():
            if field_name in ['non_field_errors', 'errors_display']:
                continue

            field = self.fields.get(field_name)
            name = getattr(field, 'label', None)

            if not name:
                # Fallback if name wasn't found
                name = field_name.replace('_', ' ').capitalize()

            for error_message in error_messages:
                formatted_errors.append(
                    _(u'{} - {}').format(_(name).capitalize(), error_message)
                )

        errors['errors_display'] = formatted_errors  # nice error message.
        return errors


class CustomSerializer(FormatErrorsSerializer):
    """
    Serializer (non-model) class to be used accross the Vita API.

    Displays pretty error messages (FormatErrorsModelSerializer)
    """


class CustomModelSerializer(FormatErrorsSerializer, PartialModelSerializer):
    """
    ModelSerializer class to be used accross the Vita API.

    Allows partial updates (PartialModelSerializer)
    Displays pretty error messages (FormatErrorsModelSerializer)
    """
