import threading
from rest_framework.throttling import BaseThrottle
from django.core.cache import cache
from datetime import timedelta
from django.core.cache import cache
from django.utils import timezone
from rest_framework.throttling import SimpleRateThrottle
from ...models import Notification


class EmailThread(threading.Thread):
    # overriding constructor
    def __init__(self, email_obj):
        # calling parent class constructor
        threading.Thread.__init__(self)
        self.email_obj = email_obj

    def run(self):
        self.email_obj.send()

class OTPRateThrottle(SimpleRateThrottle):
    scope = 'otp_login'
    rate = '1/30m'

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class IPRateLimitThrottle(SimpleRateThrottle):
    scope = 'otp_login'
    BLOCK_DURATION = 1200  # 20 minutes in seconds

    def get_cache_key(self, request, view):
        ip_address = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ip_address
        }

    def allow_request(self, request, view):
        if self.is_blocked(request):
            return False
        return super().allow_request(request, view)

    def is_blocked(self, request):
        ip_address = self.get_ident(request)
        block_time = cache.get(f'blocked_ip:{ip_address}')
        if block_time and block_time > timezone.now():
            return True
        return False

    def throttle_failure(self):
        super().throttle_failure()
        ip_address = self.get_ident(self.get_request())
        cache.set(f'blocked_ip:{ip_address}', timezone.now() + timedelta(seconds=self.BLOCK_DURATION), timeout=self.BLOCK_DURATION)

    def get_rate(self):
        return '3/minute'

def send_notification(user, message):
    """
    Utility function to create and send a notification.
    """
    notification = Notification.objects.create(user=user, message=message)
    return notification