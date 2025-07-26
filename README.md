# AI Copilot: Stateless AI Image Moderation API

## Описание

Минималистичный REST API на Django + DRF для модерации изображений с помощью OpenAI Vision (gpt-4o). База данных не используется, все запросы обрабатываются в реальном времени, без хранения данных.

## Основные эндпоинты

- **GET /copilot/health/** — Проверка работоспособности сервиса.
- **POST /copilot/ask/** — Текстовые запросы к AI (анализ текста и ответы).
- **POST /copilot/moderate-image/** — Модерация изображений через AI.

## Как работает модерация изображений

1. Клиент отправляет POST-запрос на `/copilot/moderate-image/` с изображением (поле `image` в multipart/form-data).
2. Бэкенд конвертирует изображение в base64 и отправляет его в OpenAI Vision (gpt-4o) с промптом на русском языке.
3. AI анализирует изображение на наличие опасного контента (порнография, насилие, экстремизм и т.д.) и возвращает JSON с вердиктом и объяснением.
4. Ответ API содержит поля:
   - `verdict`: `safe`, `potentially_unsafe`, `unsafe`, либо `error`.
   - `explanation`: подробное объяснение от AI.

## Пример запроса

```bash
curl -X POST http://localhost:8005/copilot/moderate-image/ \
  -F "image=@/path/to/image.jpg"
```

## Пример ответа

```json
{
  "verdict": "safe",
  "explanation": "На изображении не обнаружено опасного контента."
}
```

## Как запустить

1. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Укажите ключ OpenAI:**
   В файле `backend/settings.py` добавьте:
   ```python
   OPENAI_API_KEY = "sk-..."
   ```
3. **Запустите сервер:**
   ```bash
   python manage.py runserver 0.0.0.0:8005
   ```
   Или через Docker:
   ```bash
   docker-compose up --build
   ```

## Структура проекта

- `copilot/views.py` — эндпоинты API
- `copilot/serializers.py` — сериализаторы запросов/ответов
- `copilot/services.py` — функция анализа изображений через OpenAI
- `backend/settings.py` — настройки, включая ключ OpenAI
- `Dockerfile`, `docker-compose.yml` — для контейнеризации

## Безопасность и ограничения

- Все данные обрабатываются только в памяти, ничего не сохраняется.
- Для работы требуется валидный OpenAI API ключ с поддержкой gpt-4o и Vision.
- Не используйте для хранения персональных данных.

## Пример кода для интеграции

```python
import requests

with open('image.jpg', 'rb') as f:
    files = {'image': f}
    r = requests.post('http://localhost:8005/copilot/moderate-image/', files=files)
    print(r.json())
```
