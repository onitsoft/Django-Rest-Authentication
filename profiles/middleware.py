class CustomMiddleware(object):
    """
    Custom middleware for project

    * Set last IP and last_activity.
    """
    def process_request(self, request):
        if 'HTTP_X_REAL_IP' in request.META:
            # Get real ip if behind proxy
            #this is for prod only
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']

        user = request.user

        if user.is_authenticated():
            user.update_from_request(request)
