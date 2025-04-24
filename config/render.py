from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
import logging

class CustomJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = {
            'status': renderer_context['response'].status_code,
            'data': None,
            'error': []
        }

        if not str(response['status']).startswith('2'):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'detail':
                        response['error'].append({'key': key, 'value': value})
                    else:
                        response['error'].append({'key': key, 'value': value[0] if isinstance(value, list) else value})
            else:
                response['error'] = [{'key': item, 'value': item} for item in data]
        else:
            response['data'] = data

        rendered_data = super().render(response, accepted_media_type, renderer_context)

        response = renderer_context['response']

        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'accept, authorization, content-type,' \
                                                   ' user-agent, x-csrftoken, x-requested-with'

        return rendered_data