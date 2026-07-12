from rest_framework.views import exception_handler
from rest_framework.exceptions import ErrorDetail

def custom_api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = _create_unified_response(response)

    return response

def _create_unified_response(response):
    error_detail = _extract_error_detail(response.data)

    return {
        'success': False,
        'error': {
            'code': error_detail.get('code', 'DRF-API-ERROR'),
            'message': error_detail.get('message', 'An error occurred.'),
            'status_code': response.status_code,
        }
    }

def _extract_error_detail(error_data):
    if isinstance(error_data, str):
        return {
            'message': error_data,
            'code': 'api_error'
        }
    
    if isinstance(error_data, list) and error_data:
        first_error = error_data[0]
        if isinstance(first_error, str):
            return {
                'message': first_error, 
                'code': 'validation_error'
            }
        elif isinstance(first_error, dict):
            return _extract_error_detail(first_error)
        
    if isinstance(error_data, ErrorDetail):
        return {
            'message': str(error_data),
            'code': getattr(error_data, 'code', 'unknown_error')
        }
    
    if isinstance(error_data, dict):
        if 'message' in error_data and 'code' in error_data:
            return error_data
        
        if 'detail' in error_data:
            return {
                'message': str(error_data['detail']),
                'code': getattr(error_data['detail'], 'code', 'unknown_error')
            }
        
        field_errors = []
        for field, messages in error_data.items():
            if isinstance(messages, list) and messages:
                field_errors.append(f"{field}: {messages[0]}")
            else:
                field_errors.append(f"{field}: {str(messages)}")
        
        if field_errors:
            return {
                'message': f"{len(field_errors)} validation errors occurred",
                'code': 'validation_error',
                'errors': field_errors,
                'field_details': error_data
            }
    
    return {
        'message': str(error_data),
        'code': 'unknown_error'
    }

class BaseCustomException(Exception):
    default_detail = "An error occurred"
    default_code = "ERROR"
    status_code = 500
    
    def __init__(self, detail=None, code=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        super().__init__(self.detail)
        
# 리소스가 없는 상황에 대한 기본 예외 클래스
class ResourceNotFoundException(BaseCustomException):
    default_detail = "The requested resource was not found."
    default_code = "RESOURCE-NOT-FOUND"
    status_code = 404
    
class PostNotFoundException(ResourceNotFoundException):
    default_detail = "Post not found with the given ID."
    default_code = "POST-NOT-FOUND"
    
