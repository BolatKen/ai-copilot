
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from .serializers import ImageModerationRequestSerializer, AskRequestSerializer, AskResponseSerializer
from .services import analyze_image_with_ai
from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.conf import settings
import openai
import logging

logger = logging.getLogger(__name__)
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def moderate_image(request):
    """
    Принимает изображение, возвращает вердикт от AI (без сохранения в БД)
    """
    serializer = ImageModerationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    file = serializer.validated_data["file"]
    result = analyze_image_with_ai(file)
    return Response(result)


class HealthCheckView(APIView):
    """
    Health check endpoint для проверки состояния сервиса
    """
    @extend_schema(
        responses={200: {"description": "Service is healthy"}},
        tags=["Health"]
    )
    def get(self, request):
        return Response({
            "status": "healthy",
            "message": "Service is running properly"
        }, status=status.HTTP_200_OK)


class AskView(APIView):
    """
    API для чат-бота и анализа текста
    """
    @extend_schema(
        request=AskRequestSerializer,
        responses={200: AskResponseSerializer},
        tags=["Copilot"],
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "context": "Это текст статьи о машинном обучении...",
                    "question": "Какие основные алгоритмы упоминаются в тексте?"
                }
            )
        ]
    )




    def post(self, request):
        serializer = AskRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        context = serializer.validated_data["context"]
        question = serializer.validated_data["question"]
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ты ИИ-помощник, анализирующий текст и отвечающий на вопросы."},
                    {"role": "user", "content": f"Текст: {context}\n\nВопрос: {question}"}
                ],
                temperature=0.5,
                max_tokens=1000,
            )
            answer = response.choices[0].message.content.strip()
            return Response({"answer": answer}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in AskView: {str(e)}")
            return Response(
                {"error": "Произошла ошибка при обработке запроса"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# --- END OF FILE ---

# --- END OF FILE ---

# --- END OF FILE ---

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import AskRequestSerializer, AskResponseSerializer
from django.conf import settings
import openai
import logging

logger = logging.getLogger(__name__)
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


class HealthCheckView(APIView):
    """
    Health check endpoint для проверки состояния сервиса
    """
    @extend_schema(
        responses={200: {"description": "Service is healthy"}},
        tags=["Health"]
    )
    def get(self, request):
        return Response({
            "status": "healthy",
            "message": "Service is running properly"
        }, status=status.HTTP_200_OK)


class AskView(APIView):
    """
    API для чат-бота и анализа текста
    """
    @extend_schema(
        request=AskRequestSerializer,
        responses={200: AskResponseSerializer},
        tags=["Copilot"],
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "context": "Это текст статьи о машинном обучении...",
                    "question": "Какие основные алгоритмы упоминаются в тексте?"
                }
            )
        ]
    )

    def post(self, request):
        serializer = AskRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        context = serializer.validated_data["context"]
        question = serializer.validated_data["question"]
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ты ИИ-помощник, анализирующий текст и отвечающий на вопросы."},
                    {"role": "user", "content": f"Текст: {context}\n\nВопрос: {question}"}
                ],
                temperature=0.5,
                max_tokens=1000,
            )
            answer = response.choices[0].message.content.strip()
            return Response({"answer": answer}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in AskView: {str(e)}")
            return Response(
                {"error": "Произошла ошибка при обработке запроса"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )





import json
import os   
import re
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@extend_schema(
    tags=["Content Moderation"],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Файл для загрузки (изображение или видео)'
                }
            }
        }
    },
    responses={
        201: {
            'description': 'Файл успешно загружен и проанализирован',
            'content': {
                'application/json': {
                    'example': {
                        'content': {
                            'id': 1,
                            'file': '/media/content/example.jpg',
                            'file_type': 'image',
                            'safety_status': 'safe'
                        },
                        'message': 'Ваш контент прошел проверку на безопасность :)'
                    }
                }
            }
        },
        400: {'description': 'Ошибка валидации'}
    }
)
def upload_content(request):
    """
    API endpoint для загрузки контента (изображений и видео)
    Автоматически анализирует контент с помощью OpenAI
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'Файл не предоставлен'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    
    # Проверяем размер файла (максимум 10MB)
    if file.size > 10 * 1024 * 1024:
        return Response(
            {'error': 'Размер файла не должен превышать 10MB'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file_extension = file.name.split('.')[-1].lower()
    
    # Определяем тип файла
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
    video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm']
    
    if file_extension in image_extensions:
        file_type = 'image'
    elif file_extension in video_extensions:
        file_type = 'video'
    else:
        return Response(
            {'error': f'Неподдерживаемый тип файла: {file_extension}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Создаем объект Content
    
    # Анализируем контент с помощью AI
    # Здесь должна быть только логика для stateless AI moderation (пример):
    # result = analyze_image_with_ai(uploaded_file)
    # return Response(result)
        # try:
        #     ai_data = json.loads(ai_result)
        #     detected_tag_names = ai_data.get('detected_tags', [])
        #     safety_level = ai_data.get('safety_level', 'safe')
        # except json.JSONDecodeError:
        #     # Если AI вернул не JSON, используем значения по умолчанию
        #     detected_tag_names = []
        #     safety_level = 'safe'
        #     ai_data = {'explanation': ai_result}
        # Предполагаем, что ai_result — это str
        cleaned_result = re.sub(r'^```json\s*|\s*```$', '', ai_result.strip(), flags=re.MULTILINE)

        try:
            ai_data = json.loads(cleaned_result)
            detected_tag_names = ai_data.get('detected_tags', [])
            safety_level = ai_data.get('safety_level', 'safe')
        except json.JSONDecodeError:
        # Если не удалось распарсить, fallback
            detected_tag_names = []
            safety_level = 'safe'
            ai_data = {'explanation': ai_result}
        
        # Обновляем статус безопасности контента
        content.safety_status = safety_level
        content.save()
        
        # Создаем результат модерации
        moderation_result = ModerationResult.objects.create(
            content=content,
            ai_analysis_raw=cleaned_result
        )
        
        # Добавляем обнаруженные теги
        for tag_name in detected_tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            moderation_result.detected_tags.add(tag)
        
        # Формируем ответ
        content_serializer = ContentSerializer(content)
        moderation_serializer = ModerationResultSerializer(moderation_result)
