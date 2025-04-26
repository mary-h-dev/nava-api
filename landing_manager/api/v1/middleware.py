from django.http import HttpResponseForbidden
from ...models import AllowedIP


class RestrictIPMiddleware:
    """
    Middleware to restrict access to specific views or endpoints based on IP addresses.
    Only allows access if the request IP address is in the AllowedIP model.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
       
        restricted_path = '/api/landing_api_authorization/' 

    
        if request.path == restricted_path:
        
            ip_address = request.META.get('REMOTE_ADDR')

            if not AllowedIP.objects.filter(ip_address=ip_address).exists():
           
                return HttpResponseForbidden("Access denied: Your IP address is not allowed.")

   
        response = self.get_response(request)
        return response
