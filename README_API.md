# AI Copilot: Stateless AI Image Moderation API

## Описание

Этот проект — минималистичный REST API на Django + DRF для модерации изображений с помощью OpenAI Vision (gpt-4o). База данных не используется, все запросы обрабатываются в реальном времени, без хранения данных.

## Основные эндпоинты

- **GET /copilot/health/** — Проверка работоспособности сервиса.
- **POST /copilot/ask/** — Текстовые запросы к AI (если требуется).
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
```$ docker-compose exec web python manage.py makemigrations
Traceback (most recent call last):
  File "/app/manage.py", line 22, in <module>
    main()
  File "/app/manage.py", line 18, in main
    execute_from_command_line(sys.argv)
  File "/usr/local/lib/python3.11/site-packages/django/core/management/__init__.py", line 442, in execute_from_command_line
    utility.execute()
  File "/usr/local/lib/python3.11/site-packages/django/core/management/__init__.py", line 436, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "/usr/local/lib/python3.11/site-packages/django/core/management/base.py", line 412, in run_from_argv
    self.execute(*args, **cmd_options)
  File "/usr/local/lib/python3.11/site-packages/django/core/management/base.py", line 458, in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/django/core/management/base.py", line 106, in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/django/core/management/commands/makemigrations.py", line 213, in handle
    loader.project_state(),
    ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/django/db/migrations/loader.py", line 361, in project_state
    return self.graph.make_state(
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/django/db/migrations/graph.py", line 329, in make_state
    project_state = self.nodes[node].mutate_state(project_state, preserve=False)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/django/db/migrations/migration.py", line 91, in mutate_state
    operation.state_forwards(self.app_label, new_state)
  File "/usr/local/lib/python3.11/site-packages/django/db/migrations/operations/fields.py", line 93, in state_forwards
    state.add_field(
  File "/usr/local/lib/python3.11/site-packages/django/db/migrations/state.py", line 248, in add_field
    self.models[model_key].fields[name] = field
    ~~~~~~~~~~~^^^^^^^^^^^
KeyError: ('copilot', 'moderationresult')
