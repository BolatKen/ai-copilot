from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
import json
import os
from .models import Content, Tag, ModerationResult
from .services import ContentModerationService


class HealthCheckTestCase(APITestCase):
    """Тесты для health check эндпоинта"""
    
    def test_health_check_returns_200(self):
        """Тест что health check возвращает 200"""
        url = reverse('health-check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')


class AskViewTestCase(APITestCase):
    """Тесты для чат-бота"""
    
    @patch('copilot.views.client.chat.completions.create')
    def test_ask_view_success(self, mock_openai):
        """Тест успешного запроса к чат-боту"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Тестовый ответ"
        mock_openai.return_value = mock_response
        
        url = reverse('copilot-ask')
        data = {
            'context': 'Тестовый контекст',
            'question': 'Тестовый вопрос'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['answer'], 'Тестовый ответ')
    
    def test_ask_view_validation_error(self):
        """Тест валидации данных"""
        url = reverse('copilot-ask')
        data = {
            'context': '',  # Пустой контекст
            'question': 'Тестовый вопрос'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ContentUploadTestCase(APITestCase):
    """Тесты для загрузки контента"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем тестовое изображение
        self.test_image = SimpleUploadedFile(
            name='test.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
    
    @patch('copilot.services.ContentModerationService.analyze_image')
    def test_upload_image_success(self, mock_analyze):
        """Тест успешной загрузки изображения"""
        mock_analyze.return_value = json.dumps({
            'detected_tags': [],
            'safety_level': 'safe',
            'explanation': 'Контент безопасен'
        })
        
        url = reverse('upload_content')
        data = {'file': self.test_image}
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Content.objects.count(), 1)
        self.assertEqual(ModerationResult.objects.count(), 1)
    
    def test_upload_without_file(self):
        """Тест загрузки без файла"""
        url = reverse('upload_content')
        data = {}
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class ContentModerationServiceTestCase(TestCase):
    """Тесты для сервиса модерации контента"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.service = ContentModerationService()
    
    def test_determine_safety_status_safe(self):
        """Тест определения безопасного статуса"""
        result = self.service.determine_safety_status([])
        self.assertEqual(result, 'safe')
    
    def test_determine_safety_status_unsafe(self):
        """Тест определения небезопасного статуса"""
        result = self.service.determine_safety_status(['violence', 'pornography'])
        self.assertEqual(result, 'unsafe')
    
    def test_determine_safety_status_potentially_unsafe(self):
        """Тест определения потенциально небезопасного статуса"""
        result = self.service.determine_safety_status(['profanity'])
        self.assertEqual(result, 'potentially_unsafe')


class ModelsTestCase(TestCase):
    """Тесты для моделей"""
    
    def test_tag_creation(self):
        """Тест создания тега"""
        tag = Tag.objects.create(name='test_tag')
        self.assertEqual(str(tag), 'test_tag')
    
    def test_content_creation(self):
        """Тест создания контента"""
        content = Content.objects.create(
            file='test.jpg',
            file_type='image'
        )
        self.assertEqual(content.file_type, 'image')
        self.assertEqual(content.safety_status, 'safe')
    
    def test_moderation_result_creation(self):
        """Тест создания результата модерации"""
        content = Content.objects.create(
            file='test.jpg',
            file_type='image'
        )
        result = ModerationResult.objects.create(
            content=content,
            ai_analysis_raw='{"test": "data"}'
        )
        self.assertEqual(result.content, content)
        self.assertFalse(result.is_checked_by_moderator)


class ModeratorAPITestCase(APITestCase):
    """Тесты для API модератора"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.content = Content.objects.create(
            file='test.jpg',
            file_type='image'
        )
        self.moderation_result = ModerationResult.objects.create(
            content=self.content,
            ai_analysis_raw='{"test": "data"}'
        )
    
    def test_get_unverified_content(self):
        """Тест получения непроверенного контента"""
        url = reverse('get_unverified_content')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_mark_as_verified(self):
        """Тест пометки контента как проверенного"""
        url = reverse('mark_as_verified', args=[self.moderation_result.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.moderation_result.refresh_from_db()
        self.assertTrue(self.moderation_result.is_checked_by_moderator)
    
    def test_update_moderation_tags(self):
        """Тест обновления тегов модерации"""
        url = reverse('update_moderation_tags', args=[self.content.id])
        data = {
            'moderator_tags': 'tag1, tag2',
            'moderator_verdict': 'Безопасный контент'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.moderation_result.refresh_from_db()
        self.assertEqual(self.moderation_result.moderator_tags, 'tag1, tag2')
        self.assertEqual(self.moderation_result.moderator_verdict, 'Безопасный контент')
