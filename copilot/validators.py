from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
import os


def validate_file_size(value):
    """Валидация размера файла (максимум 10MB)"""
    limit = 10 * 1024 * 1024  # 10MB
    if value.size > limit:
        raise ValidationError(
            _('Размер файла не должен превышать %(limit)s.'),
            params={'limit': '10MB'}
        )


def validate_image_file(value):
    """Валидация типа файла для изображений"""
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
    ext = os.path.splitext(value.name)[1][1:].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            _('Неподдерживаемый тип файла. Разрешены: %(extensions)s'),
            params={'extensions': ', '.join(allowed_extensions)}
        )


def validate_video_file(value):
    """Валидация типа файла для видео"""
    allowed_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm']
    ext = os.path.splitext(value.name)[1][1:].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            _('Неподдерживаемый тип файла. Разрешены: %(extensions)s'),
            params={'extensions': ', '.join(allowed_extensions)}
        )


def validate_openai_response(response_text):
    """Валидация ответа от OpenAI API"""
    if not response_text or len(response_text.strip()) == 0:
        raise ValidationError(_('Получен пустой ответ от AI'))
    
    if len(response_text) > 10000:
        raise ValidationError(_('Ответ от AI слишком длинный'))
    
    return response_text.strip()


def validate_moderation_tags(tags_string):
    """Валидация строки с тегами модератора"""
    if not tags_string:
        return tags_string
    
    # Разделяем по запятым и очищаем
    tags = [tag.strip() for tag in tags_string.split(',')]
    
    # Убираем пустые теги
    tags = [tag for tag in tags if tag]
    
    # Проверяем длину каждого тега
    for tag in tags:
        if len(tag) > 50:
            raise ValidationError(
                _('Тег "%(tag)s" слишком длинный (максимум 50 символов)'),
                params={'tag': tag}
            )
    
    return ', '.join(tags)
