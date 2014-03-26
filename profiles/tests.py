from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from .admin import UserCreationForm, UserAdmin
from .models import User
from .serializers import UserSerializer


class UserTestCase(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email='test@example.com', password='test')

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = User.objects.create_superuser(email='test@example.com', password='test')

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_names(self):
        first_name = 'test'
        last_name = 'user'
        email = 'test@example.com'

        user1 = User(first_name=first_name, last_name=last_name)
        user2 = User(email=email)

        self.assertIn('test user', user1.get_full_name())
        self.assertIn(email, user2.get_full_name())
        self.assertIn(first_name, user1.get_short_name())
        self.assertIn(email, user2.get_short_name())

    def test_geoip(self):
        user = User.objects.create(email='test@example.com')

        user.registration_ip = '37.26.147.250'
        user.set_country_by_ip()

        self.assertEquals(user.location.country, 'IL')
        self.assertEquals(user.location.country.name, 'Israel')

    def test_guessing_timezone(self):
        user = User.objects.create(email='test@example.com')

        user.location.country = 'IL'
        user.location.save()

        user.set_timezone_by_country()
        self.assertEquals(str(user.timezone), 'Asia/Jerusalem')


class UserSerializerTestCase(TestCase):
    def test_serializer_validate_password_ok(self):
        serializer = UserSerializer(data={
            'email': 'test@example.com',
            'first_name': 'test',
            'last_name': 'test',
            'password': '123456',
        })
        self.assertTrue(serializer.is_valid())

    def test_serializer_validate_password_too_short(self):
        serializer = UserSerializer(data={
            'email': 'test@example.com',
            'first_name': 'test',
            'last_name': 'test',
            'password': '1234',
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)


class UserAdminTestCase(TestCase):
    def test_create_form_validate_password2(self):
        form = UserCreationForm(data={
            'email': 'test@example.com',
            'password1': 'one',
            'password2': 'two',
        })

        self.assertEquals(form.is_valid(), False)
        self.assertEquals(form.errors['password2'], ["Passwords don't match"])
        self.assertEquals(len(form.errors['password2']), 1)  # no other errors

    def test_create_form_success(self):
        form = UserCreationForm(data={
            'email': 'test@example.com',
            'password1': 'okpassword',
            'password2': 'okpassword',
        })

        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_password_change_link(self):
        user = User()
        useradmin = UserAdmin(user, AdminSite())

        self.assertIn('password/', useradmin.change_password(user))

    def test_close_user_accounts_action(self):
        useradmin = UserAdmin(User, AdminSite())
        User.objects.create(email='test@example.com')

        useradmin.close_user_account(None, User.objects.all())

        self.assertEquals(User.objects.get().status, User.Status.CLOSED)

    @classmethod
    def tearDownClass(cls):
        try:
            admin.site.unregister(User)
        except Exception:
            pass
