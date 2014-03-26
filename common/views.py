from rest_framework import generics, response, permissions

from .viewsets import UpdateUserMixin

import vita_auth


class APIRootView(generics.GenericAPIView, UpdateUserMixin):
    permission_classes = (permissions.AllowAny, )

    def get(self, request):
        return response.Response({'name': 'VitaPersonal API', 'version': vita_auth.__version__})
