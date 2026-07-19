from django.http import JsonResponse
from django.http import Http404
from django.core.exceptions import PermissionDenied
from config.custom_exceptions import BaseCustomException

class ExceptionHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        error_info = self._get_error_info(exception)

        response_data = self._create_unified_response(request, error_info)

        return JsonResponse(
            response_data,
            status=error_info['status_code'] if 'status_code' in error_info else 500,
        )
    
    def _get_error_info(self, exception):
		# 커스텀 예외 
        if isinstance(exception, BaseCustomException):
            return {
                'message': exception.detail,
                'status_code': exception.status_code,
                'code': exception.code
            }

            # 기타 예외
        return {
            'message': 'An internal server error occurred.',
            'status_code': 500,
            'code': 'INTERNAL-SERVER-ERROR'
        }
    
        
    def _create_unified_response(self, request, error_info):
        return {
            'success': False,
            'error': {
                'code': error_info.get('code', 'UNKNOWN_ERROR'),
                'message': error_info.get('message', 'An error occurred.'),
                'status_code': error_info.get('status_code', 500),
            }
        }