from django.conf.urls import url, include
from rest_framework import routers
from common.views import APIRootView
from profiles.views import (UserViewSet, LoginView, LogoutView,
                            PasswordResetView,
                            PasswordResetCompleteView,
                            ProfileViewSet)


class CustomRouter(routers.SimpleRouter):
    """Make trailing slash optional"""
    def __init__(self, *args, **kwargs):
        super(CustomRouter, self).__init__(*args, **kwargs)
        self.trailing_slash = '/?'

router = CustomRouter()

router.register(r'users', UserViewSet, base_name='user')
router.register(r'profiles', ProfileViewSet, base_name='profile')
# NOTE: hacky way to represent nested current/user items
# router.register(r'users/(?P<user_id>[\d]+|me)/profiles', ProfilesViewSet)


urlpatterns = [
    url(r'', APIRootView.as_view(), name="root"),
    url(r'^login/?$', LoginView.as_view(), name='login'),
    url(r'^logout/?$', LogoutView.as_view(), name='logout'),
    url(r'^password_reset/?$', PasswordResetView.as_view()),
    url(r'^password_reset_complete/?$', PasswordResetCompleteView.as_view()),
    # url(r'^check_version', CheckVersionView.as_view()),
    url(r'^', include(router.urls)),
]
