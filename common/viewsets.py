from rest_framework import mixins, viewsets


class UpdateUserMixin(object):
    def perform_authentication(self, request):
        """
        Overriding the default method, to update the users details after
        the request.
        """
        if request.user.is_authenticated():
            # request.user.authenticate()
            # request.user.update_from_request(request)
            pass


class NoDeleteModelViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           UpdateUserMixin,
                           viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, and `list()` actions.

    Like ModelViewSet but without DELETE ("destroy()").

    Also includes the UpdateUserMixin.
    """
