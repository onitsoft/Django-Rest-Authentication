from django.core.exceptions import ValidationError
from django.test import TestCase

from common.fields import EmailListField


class EmailListFieldTestCase(TestCase):
    def test_email_field_from_to_native(self):
        f = EmailListField()
        data = ['t@example.com', 't2@example.com']
        self.assertEquals(f.from_native(data), data)
        self.assertEquals(f.to_native(data), data)

    def test_validation(self):
        f = EmailListField()

        def _validate(value):
            try:
                f.validate(value)
                f.run_validators(value)
            except ValidationError:
                return False
            return True

        self.assertTrue(_validate(['t@example.com']))
        self.assertTrue(_validate(['t@example.com', 't2@example.com']))

        self.assertFalse(_validate([]))
        self.assertFalse(_validate(['t@example.com', 'invalid']))
        self.assertFalse(_validate(['t@example.com', 1]))
        self.assertFalse(_validate(['t@example.com', None]))
        self.assertFalse(_validate(['t@example.com', '']))
        self.assertFalse(_validate('abc'))
        self.assertFalse(_validate(None))
