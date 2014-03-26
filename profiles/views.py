from django.conf import settings
from django.contrib.auth import login, logout
from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.response import Response

from common.viewsets import NoDeleteModelViewSet

from .serializers import (UserSerializer, AuthenticationSerializer,
                          PasswordResetSerializer,
                          PasswordResetCompleteSerializer,
                          MedicalProfileSerializer)
from .models import User, PasswordResetRequest, MedicalProfile


class CustomUserPermissions(BasePermission):
    """
    Custom permission class for the users API.

    * Anyone can create a user.
    * Any user can retrieve/update himself.
    * An admin can terrieve/update all users.
    * Delete is forbidden for everyone.
    """

    def has_permission(self, request, view):
        """
        Anyone can create.
        Listing will be limited by get_queryset()
        """
        if not request.user.is_authenticated() and view.kwargs.get('pk') == 'me':
            # workaround for /users/me - lookup happening before has_object_permission()
            return False

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not request.user.is_authenticated():
            return False

        if user.is_superuser or user == obj:
            return True  # a superuser can access any object

        if request.method not in SAFE_METHODS:
            return False

        if user.is_staff():
            # If a user that's in the staff can safely access any object
            return True

        return False


class MedicalProfileViewSet(NoDeleteModelViewSet):
    """
    /users/me/profiles or  /users/profiles
    """
    model = MedicalProfile
    serializer_class = MedicalProfileSerializer
    permission_classes = (CustomUserPermissions, )

class UserViewSet(NoDeleteModelViewSet):
    model = User
    serializer_class = UserSerializer
    permission_classes = (CustomUserPermissions, )

    def get_object(self):
        """
        Handle regular lookup, and /users/me/
        """
        lookup = self.kwargs.get(self.lookup_field)
        if lookup == 'me':
            lookup = getattr(self.request.user, self.lookup_field, None)
            self.kwargs[self.lookup_field] = lookup

        return super(UserViewSet, self).get_object()

    def get_queryset(self):
        """Limit the queryset for listing only"""
        queryset = super(UserViewSet, self).get_queryset()

        # optimization:

        if self.action != 'list' or self.request.user.is_superuser:
            return queryset

        user = self.request.user

        if not user.is_authenticated():
            return []

        if user.is_staff():
            return queryset.filter()

        return queryset.filter(pk=self.request.user.pk)

    def post_save(self, obj, created):
        """
        Save registration ip and log the user in.
        """
        super(UserViewSet, self).post_save(obj, created)
        user = obj

        if created and obj.registration_ip:
            user.set_country_by_ip()
            user.set_timezone_by_country()
            user.save()

        # login the user on creation
        if not self.request.user.is_authenticated() and created:
            # hack to set the auth backend to log the user in:
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login(self.request, user)


class ProfilesViewSet(NoDeleteModelViewSet):
    pass


class UserRolePermission(BasePermission):
    def has_permission(self, request, view):
        """Hackery to allow only /users/me/ or /users/<current_id>/ to access"""
        if view.kwargs['user_id'] in ['me', str(request.user.id)]:
            return True
        return False


class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = AuthenticationSerializer

    def post(self, request):

        if request.user.is_authenticated():
            return Response({'non_field_errors': [_('Already logged in.')]},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.DATA)

        if serializer.is_valid():
            user = serializer.user
            login(request, user)

            return Response({'result': _('Login successful')})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AuthenticationSerializer

    def logout(self, request):
        """Logout helper method"""
        logout(request)
        return Response({'result': _('Logged out')})

    get = logout   # bind get and post to the logout 'view'
    post = logout


class PasswordResetView(generics.GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA, context={'request': request})

        if serializer.is_valid():
            user = serializer._user  # cached user
            PasswordResetRequest.objects.filter(user=user).delete()  # delete previous entries
            PasswordResetRequest.objects.create(user=user)

            return Response({'result': _('Please check your E-mail')})

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetCompleteView(generics.GenericAPIView):
    """
    View for setting a new password provided an password reset token.
    """
    permission_classes = (AllowAny, )
    serializer_class = PasswordResetCompleteSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA, context={'request': request})

        if serializer.is_valid():
            user = serializer._user  # cached user
            PasswordResetRequest.objects.filter(user=user).delete()  # delete previous entries

            # change the password
            user.set_password(serializer.data['password'])
            user.save()

            # Log the user in
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user)

            return Response({'result': _('Password reset successful')})

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SocialAuthView(TemplateView):
    """Temporary view for testing"""
    pass
    # raise Exception("Not implemented")
