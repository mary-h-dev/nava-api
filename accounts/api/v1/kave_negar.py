import requests
import json
from django.conf import settings

# Default requests timeout in seconds.
DEFAULT_TIMEOUT = 10


class APIException(Exception):
    def __init__(self, message, code, errors):
        super().__init__(message)
        self.code = code
        self.errors = errors


class HTTPException(Exception):
    pass


class KavenegarAPI(object):
    def __init__(self, timeout=None):
        self.version = 'v1'
        self.host = 'api.kavenegar.com'
        self.apikey = settings.SMS_API_KEY
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8'
        }

    def __repr__(self):
        return "kavenegar.KavenegarAPI({!r})".format(self.apikey)

    def __str__(self):
        return "kavenegar.KavenegarAPI({!s})".format(self.apikey)

    def _request(self, action, method, params={}):
        url = 'https://' + self.host + '/' + self.version + '/' + self.apikey + '/' + action + '/' + method + '.json'
        try:
            content = requests.post(url, headers=self.headers, auth=None, data=params, timeout=self.timeout).content
            try:
                response = json.loads(content.decode("utf-8"))
                if (response['return']['status'] == 200):
                    response = response['entries']
                else:
                    raise APIException('API-Exception', response['return']['status'], response['return']['message'])
            except ValueError as e:
                raise HTTPException(e)
            return (response)
        except requests.exceptions.RequestException as e:
            raise HTTPException(e)

    def sms_send(self, receptor, message, sender):
        params = {
            'receptor': receptor,
            'message': message,
            'sender': sender,
        }
        return self._request('sms', 'send', params)


def sms_90009809(mobile, message):
    cls = KavenegarAPI()
    try:
        res = cls.sms_send(mobile, message, '90009809')
    except APIException as e:
        res = e.errors
    except Exception as e:
        res = str(e)
    if isinstance(res, str):
        raise Exception(res)
    return res
