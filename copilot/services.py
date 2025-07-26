import base64
from PIL import Image
from io import BytesIO
import openai
from django.conf import settings
import re
import json

def analyze_image_with_ai(image_file):
    """
    Принимает InMemoryUploadedFile, возвращает вердикт и объяснение от OpenAI Vision
    """
    # Преобразуем изображение в base64
    img = Image.open(image_file)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    dangerous_tags = [
        'pornography', 'violence', 'profanity', 'dangerous_symbols', 'hate_speech',
        'weapons', 'drugs', 'self_harm', 'extremism', 'nudity', 'sexual_content',
        'graphic_violence', 'blood', 'disturbing_content'
    ]
    prompt = (
        "Проанализируй это изображение на наличие опасного контента и пригодность для краудфандинговой платформы (например, Kickstarter). Не пиши в ответе каких тегов ты не нашел."
        f"Верни результат в формате JSON со следующими полями: "
        f"'verdict': safe/potentially_unsafe/unsafe, 'explanation': объяснение. "
        f"Опасные теги: {', '.join(dangerous_tags)}. "
        "safe — полностью безопасно, potentially_unsafe — есть сомнительные элементы, unsafe — явно опасно. "
        "Поле 'explanation' должно включать как обоснование по безопасности, так и краткий совет по улучшению изображения с точки зрения краудфандинга (например: композиция, фон, доверие, профессиональность)."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }
        ],
        max_tokens=300
    )
    try:
        content = response.choices[0].message.content
        # Убираем блоки ```json ... ```
        match = re.search(r'```json\s*(\{.*\})\s*```', content, re.DOTALL)
        if match:
            content = match.group(1)
        result = json.loads(content)
        return {
            "verdict": result.get("verdict", "unknown"),
            "explanation": result.get("explanation", "")
        }
    except Exception:
        return {
            "verdict": "error",
            "explanation": response.choices[0].message.content
        }
