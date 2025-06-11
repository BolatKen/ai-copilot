import os
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
from django.conf import settings

class ContentModerationService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Список опасных тегов для модерации
        self.dangerous_tags = [
            'pornography',
            'violence',
            'profanity',
            'dangerous_symbols',
            'hate_speech',
            'weapons',
            'drugs',
            'self_harm',
            'extremism'
        ]
    
    def encode_image(self, image_path):
        """Кодирует изображение в base64 для отправки в OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_image(self, image_path):
        """Анализирует изображение на наличие опасного контента"""
        try:
            base64_image = self.encode_image(image_path)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Проанализируй это изображение на наличие опасного контента. 
                                Верни результат в формате JSON со следующими полями:
                                - "detected_tags": список обнаруженных опасных тегов из списка: {', '.join(self.dangerous_tags)}
                                - "safety_level": "safe", "potentially_unsafe" или "unsafe"
                                - "explanation": краткое объяснение решения
                                
                                Критерии оценки:
                                - "safe": контент полностью безопасен
                                - "potentially_unsafe": есть сомнительные элементы, но не критично
                                - "unsafe": явно опасный контент
                                """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Ошибка анализа изображения: {str(e)}"
    
    def analyze_video_frame(self, video_path):
        """Анализирует кадр из видео (упрощенная версия - анализ первого кадра)"""
        # Для полноценного анализа видео потребуется извлечение кадров
        # Здесь показан пример для одного кадра
        try:
            # В реальной реализации здесь должно быть извлечение кадра из видео
            # Например, с помощью opencv-python или ffmpeg
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": f"""Проанализируй видео контент на наличие опасных материалов.
                        Верни результат в формате JSON со следующими полями:
                        - "detected_tags": список обнаруженных опасных тегов из списка: {', '.join(self.dangerous_tags)}
                        - "safety_level": "safe", "potentially_unsafe" или "unsafe"
                        - "explanation": краткое объяснение решения
                        
                        Критерии оценки:
                        - "safe": контент полностью безопасен
                        - "potentially_unsafe": есть сомнительные элементы, но не критично
                        - "unsafe": явно опасный контент
                        
                        Файл видео: {video_path}
                        """
                    }
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Ошибка анализа видео: {str(e)}"
    
    def determine_safety_status(self, detected_tags):
        """Определяет статус безопасности на основе обнаруженных тегов"""
        if not detected_tags:
            return 'safe'
        
        # Критические теги, которые сразу делают контент небезопасным
        critical_tags = ['pornography', 'violence', 'hate_speech', 'extremism']
        
        if any(tag in critical_tags for tag in detected_tags):
            return 'unsafe'
        elif len(detected_tags) > 0:
            return 'potentially_unsafe'
        else:
            return 'safe'

