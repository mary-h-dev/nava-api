from django.conf import settings
from django.http import HttpResponseForbidden
from functools import wraps



def restrict_ip(view_func):
    """
    Decorator to restrict view access to certain IP addresses.
    Only allows access if the request IP address is in the ALLOWED_IPS list from settings.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        ip_address = request.META.get('REMOTE_ADDR')

        if ip_address not in settings.ALLOWED_IPS:
            return HttpResponseForbidden("Access denied: Your IP address is not allowed.")


        return view_func(request, *args, **kwargs)

    return _wrapped_view
