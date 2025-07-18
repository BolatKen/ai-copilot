from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class OpenAIAPIException(Exception):
    """Исключение для ошибок OpenAI API"""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ContentModerationException(Exception):
    """Исключение для ошибок модерации контента"""
    def __init__(self, message, content_id=None):
        self.message = message
        self.content_id = content_id
        super().__init__(self.message)


class FileValidationException(Exception):
    """Исключение для ошибок валидации файлов"""
    def __init__(self, message, file_name=None):
        self.message = message
        self.file_name = file_name
        super().__init__(self.message)


def custom_exception_handler(exc, context):
    """Кастомный обработчик исключений"""
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': 'Произошла ошибка при выполнении запроса',
            'details': response.data,
            'status_code': response.status_code
        }
        
        # Логируем ошибку
        logger.error(f"API Error: {response.status_code} - {response.data}")
        
        response.data = custom_response_data
    
    # Обработка кастомных исключений
    if isinstance(exc, OpenAIAPIException):
        logger.error(f"OpenAI API Error: {exc.message}")
        return Response({
            'error': True,
            'message': 'Ошибка при обращении к AI сервису',
            'details': exc.message,
            'status_code': exc.status_code
        }, status=exc.status_code)
    
    if isinstance(exc, ContentModerationException):
        logger.error(f"Content Moderation Error: {exc.message}")
        return Response({
            'error': True,
            'message': 'Ошибка при модерации контента',
            'details': exc.message,
            'content_id': exc.content_id,
            'status_code': 400
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(exc, FileValidationException):
        logger.error(f"File Validation Error: {exc.message}")
        return Response({
            'error': True,
            'message': 'Ошибка валидации файла',
            'details': exc.message,
            'file_name': exc.file_name,
            'status_code': 400
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return response
