from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import AskRequestSerializer, AskResponseSerializer
from django.conf import settings
import openai

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

class AskView(APIView):

    @extend_schema(
        request=AskRequestSerializer,
        responses={200: AskResponseSerializer},
        tags=["Copilot"]
    )
    def post(self, request):
        context = request.data.get("context")
        question = request.data.get("question")

        if not context or not question:
            return Response({"error": "Missing context or question"}, status=400)

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ты ИИ-помощник, анализирующий текст и отвечающий на вопросы."},
                    {"role": "user", "content": f"Текст: {context}\n\nВопрос: {question}"}
                ],
                temperature=0.5,
            )
            answer = response.choices[0].message.content.strip()
            return Response({"answer": answer})

        except Exception as e:
            return Response({"error": str(e)}, status=500)





import json
import os   
import re
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Content, Tag, ModerationResult
from .serializers import ContentSerializer, ModerationResultSerializer
from .services import ContentModerationService
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_content(request):
    """
    API endpoint для загрузки контента (изображений и видео)
    Автоматически анализирует контент с помощью OpenAI
    """
    if 'file' not in request.FILES:
        return Response({'error': 'Файл не предоставлен'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    file_extension = file.name.split('.')[-1].lower()
    
    # Определяем тип файла
    image_extensions = ['jpg', 'jpeg', 'png', 'svg']
    video_extensions = ['mp4', 'mov']
    
    if file_extension in image_extensions:
        file_type = 'image'
    elif file_extension in video_extensions:
        file_type = 'video'
    else:
        return Response({'error': 'Неподдерживаемый тип файла'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Создаем объект Content
    content = Content.objects.create(
        file=file,
        file_type=file_type
    )
    
    # Анализируем контент с помощью AI
    moderation_service = ContentModerationService()
    
    try:
        if file_type == 'image':
            ai_result = moderation_service.analyze_image(content.file.path)
        else:  # video
            ai_result = moderation_service.analyze_video_frame(content.file.path)
        
        # # Парсим результат AI (предполагаем JSON формат)
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
        
        return Response({
            'content': content_serializer.data,
            'moderation_result': moderation_serializer.data,
            'message': get_safety_message(safety_level)
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        # В случае ошибки AI анализа, сохраняем контент как безопасный
        content.safety_status = 'safe'
        content.save()
        
        return Response({
            'content': ContentSerializer(content).data,
            'error': f'Ошибка анализа: {str(e)}',
            'message': 'Ваш контент прошел проверку на безопасность :)'
        }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_content_status(request, content_id):
    """
    API endpoint для получения статуса модерации контента
    """
    try:
        content = Content.objects.get(id=content_id)
        moderation_result = getattr(content, 'moderation_result', None)
        
        response_data = {
            'content': ContentSerializer(content).data,
            'message': get_safety_message(content.safety_status)
        }
        
        if moderation_result:
            response_data['moderation_result'] = ModerationResultSerializer(moderation_result).data
        
        return Response(response_data)
        
    except Content.DoesNotExist:
        return Response({'error': 'Контент не найден'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def moderator_dashboard(request):
    """
    API endpoint для модераторов - получение списка контента для модерации
    """
    safety_filter = request.GET.get('safety_status', None)
    
    queryset = Content.objects.all().order_by('-uploaded_at')
    
    if safety_filter:
        queryset = queryset.filter(safety_status=safety_filter)
    
    # Группируем по статусам для удобства модератора
    content_by_status = {
        'safe': [],
        'potentially_unsafe': [],
        'unsafe': []
    }
    
    for content in queryset:
        content_data = ContentSerializer(content).data
        try:
            moderation_result = content.moderation_result
            content_data['moderation_result'] = ModerationResultSerializer(moderation_result).data
        except:
            content_data['moderation_result'] = None
            
        content_by_status[content.safety_status].append(content_data)
    
    return Response({
        'content_by_status': content_by_status,
        'total_count': queryset.count(),
        'status_counts': {
            'safe': len(content_by_status['safe']),
            'potentially_unsafe': len(content_by_status['potentially_unsafe']),
            'unsafe': len(content_by_status['unsafe'])
        }
    })

@api_view(['POST'])
def update_content_status(request, content_id):
    """
    API endpoint для модераторов - обновление статуса контента
    """
    try:
        content = Content.objects.get(id=content_id)
        new_status = request.data.get('safety_status')
        
        if new_status not in ['safe', 'potentially_unsafe', 'unsafe']:
            return Response({'error': 'Неверный статус'}, status=status.HTTP_400_BAD_REQUEST)
        
        content.safety_status = new_status
        content.save()
        
        return Response({
            'content': ContentSerializer(content).data,
            'message': f'Статус обновлен на: {get_safety_message(new_status)}'
        })
        
    except Content.DoesNotExist:
        return Response({'error': 'Контент не найден'}, status=status.HTTP_404_NOT_FOUND)

def get_safety_message(safety_status):
    """
    Возвращает сообщение для пользователя в зависимости от статуса безопасности
    """
    messages = {
        'safe': 'Ваш контент прошел проверку на безопасность :)',
        'potentially_unsafe': 'В вашем контенте могут содержаться опасные материалы :O',
        'unsafe': 'Ваш контент содержит опасные материалы :('
    }
    return messages.get(safety_status, 'Статус неизвестен')

@api_view(['GET'])
def get_submission_warning(request, content_id):
    """
    API endpoint для получения предупреждения перед отправкой на модерацию
    """
    try:
        content = Content.objects.get(id=content_id)
        
        if content.safety_status == 'potentially_unsafe':
            return Response({
                'show_warning': True,
                'warning_message': 'Перед тем как отправить файл просим вас еще раз проверить содержимое вашего контента, при отправке опасных материалов на модерацию. Администрация платформы оставляет за собой право забанить ваш аккаунт!'
            })
        else:
            return Response({
                'show_warning': False,
                'message': 'Контент готов к отправке на модерацию'
            })
            
    except Content.DoesNotExist:
        return Response({'error': 'Контент не найден'}, status=status.HTTP_404_NOT_FOUND)



from django.http import JsonResponse
from .models import ModerationResult
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.forms.models import model_to_dict



@csrf_exempt
def get_unverified_content(request):
    results = ModerationResult.objects.filter(is_checked_by_moderator=False).select_related('content')
    data = []
    for result in results:
        item = {
            "id": result.content.id,
            "file": result.content.file.url,
            "file_type": result.content.file_type,
            "uploaded_at": result.content.uploaded_at,
            "safety_status": result.content.safety_status,
            "moderation_result": {
                "id": result.id,
                "analyzed_at": result.analyzed_at,
                "detected_tags": [tag.name for tag in result.detected_tags.all()],
                "ai_analysis_raw": result.ai_analysis_raw,
                "is_checked_by_moderator": result.is_checked_by_moderator,
                "moderator_tags": result.moderator_tags or " "  # 👈 ДОБАВЬ ЭТО
            }
        }
        data.append(item)
    return JsonResponse(data, safe=False)


@csrf_exempt
def mark_as_verified(request, result_id):
    if request.method == 'POST':
        result = ModerationResult.objects.get(pk=result_id)
        result.is_checked_by_moderator = True
        result.save()
        return JsonResponse({'status': 'safe'})
    
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
@api_view(['POST'])
def update_moderation_tags(request, content_id):
    """
    Обновляет теги и вердикт модератора
    """
    try:
        content = Content.objects.get(id=content_id)
        moderation_result = content.moderation_result

        # Получаем данные
        moderator_tags = request.data.get('moderator_tags', '')
        moderator_verdict = request.data.get('moderator_verdict', '')

        # Обновляем
        moderation_result.moderator_tags = moderator_tags
        moderation_result.moderator_verdict = moderator_verdict
        moderation_result.save()

        return Response({
            'message': 'Теги и вердикт успешно обновлены.',
            'moderation_result': {
                'moderator_tags': moderation_result.moderator_tags,
                'moderator_verdict': moderation_result.moderator_verdict,
            }
        })
    except Content.DoesNotExist:
        return Response({'error': 'Контент не найден'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
def moderator_finalize_review(request, content_id):
    try:
        content = Content.objects.get(id=content_id)
        result = content.moderation_result

        # Обновляем статус
        status_val = request.data.get('safety_status')
        if status_val not in ['safe', 'potentially_unsafe', 'unsafe']:
            return Response({'error': 'Неверный статус'}, status=status.HTTP_400_BAD_REQUEST)
        content.safety_status = status_val
        content.save()

        # Обновляем теги и вердикт
        result.moderator_tags = request.data.get('moderator_tags', '')
        result.moderator_verdict = request.data.get('moderator_verdict', '')
        result.is_checked_by_moderator = True
        result.save()

        return Response({'message': 'Контент успешно модерирован.'})
    except Content.DoesNotExist:
        return Response({'error': 'Контент не найден'}, status=status.HTTP_404_NOT_FOUND)
