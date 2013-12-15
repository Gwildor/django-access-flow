from django.core.exceptions import PermissionDenied
from django.views import generic


class SecuredView(object):
    access_checks = []

    def get_access_checks(self):
        return self.access_checks

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

        access_response = self.check_access()
        if not self.grant_access(access_response):
            return self.access_denied(access_response, *args, **kwargs)

        return super(SecuredView, self).dispatch(request, *args, **kwargs)

    def check_access(self):
        """Check access, and return something to be returned to grant_access.

        By default, you can return None, True or an empty iterable to grant
        access. An iterable of reasons why access was denied should be returned
        when access shouldn't be granted, which can be used in
        access_denied to build a response.
        """

        if hasattr(self, 'model'):
            # We want self.model for CreateView, ListView and other model
            # views. Luckily, SingleObjectMixin.get_object() raises an
            # AttributeError if no pk or slug is provided in the kwargs, and so
            # does calling a method which does not exist at all, so catching
            # AttributeError is fine.
            access_args = [self.get_access_checks(), self.request.user]
            try:
                self.object = self.get_object()
                denied = self.object.check_access(*access_args)
            except AttributeError:
                denied = self.model.check_access(self.model(), *access_args)

            return denied

    def grant_access(self, access_response):
        """Decide if access should be granted, based on value of check_access.

        Custom decisions can be defined here if you have a special
        check_access, although the main reason this method was created was
        because the single line if statement became too complex for the
        dispatch method to handle.
        """

        if access_response is None:
            return True

        if access_response is True:
            return True

        try:
            if len(access_response) == 0:
                return True
        except TypeError:
            pass

        return False

    def access_denied(self, denied, *args, **kwargs):
        """Return an access denied response to be returned to the browser.

        Based on the return value of check_access, you can implement special
        messages, pages or redirects.

        By default, return a HTTP 403 Forbidden error response, thanks to the
        PermissionDenied exception.
        """

        raise PermissionDenied
