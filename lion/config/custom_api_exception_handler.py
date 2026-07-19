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
