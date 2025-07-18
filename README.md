# AI-Copilot

Система искусственного интеллекта с тремя основными функциями:

1. **Чат-бот** - Интерактивный ИИ-помощник для общения с пользователями
2. **Copilot** - Анализ выделенного текста и ответы на вопросы по контексту
3. **Модерация контента** - Автоматическая проверка загружаемых изображений и видео

## Функциональность

### 🤖 Чат-бот

- Интеллектуальные ответы на вопросы пользователей
- Контекстное понимание диалога
- Поддержка различных тем

### 📝 Copilot

- Анализ выделенного текста на странице
- Ответы на вопросы по контексту
- Объяснение сложных концепций

### 🛡️ Модерация контента

- Автоматическая проверка изображений и видео
- Обнаружение опасного контента
- Панель администратора для ручной модерации
- Система тегов и классификации

## Установка

1. Клонируйте репозиторий:

```bash
git clone <repository-url>
cd ai-copilot
```

2. Создайте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

5. Заполните переменные окружения в `.env`:

```
DJANGO_SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

6. Примените миграции:

```bash
python manage.py migrate
```

7. Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

8. Запустите сервер:

```bash
python manage.py runserver
```

## API Endpoints

### Чат-бот и Copilot

- `POST /copilot/ask/` - Отправка вопроса с контекстом
- `GET /copilot/health/` - Проверка здоровья сервиса

### Модерация контента

- `POST /copilot/upload/` - Загрузка файла для модерации
- `GET /copilot/content/<id>/status/` - Получение статуса модерации
- `GET /copilot/content/<id>/warning/` - Получение предупреждения
- `POST /copilot/content/<id>/update-status/` - Обновление статуса (модератор)

### Панель модератора

- `GET /copilot/moderator/dashboard/` - Панель модератора
- `GET /copilot/unverified/` - Непроверенный контент
- `POST /copilot/moderation/<id>/verify/` - Подтверждение модерации
- `POST /copilot/moderation/<id>/update-tags/` - Обновление тегов
- `POST /copilot/moderation/finalize/<id>/` - Завершение модерации

## Документация API

После запуска сервера документация доступна по адресам:

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI схема: `http://localhost:8000/api/schema/`

## Структура проекта

```
ai-copilot/
├── backend/              # Настройки Django
├── copilot/              # Основное приложение
│   ├── models.py         # Модели данных
│   ├── views.py          # API endpoints
│   ├── serializers.py    # Сериализаторы DRF
│   ├── services.py       # Сервисы для работы с OpenAI
│   └── urls.py           # URL маршруты
├── content/              # Загруженные файлы
├── requirements.txt      # Зависимости Python
├── manage.py            # Django управление
└── README.md            # Документация
```

## Разработка

### Запуск в режиме разработки

```bash
python manage.py runserver
```

### Запуск тестов

```bash
python manage.py test
```

### Создание миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

## Безопасность

- Все API endpoints защищены от CSRF атак
- Файлы проверяются на размер и тип
- Контент автоматически анализируется на безопасность
- Настроены CORS для фронтенда

## Поддержка

Для вопросов и предложений создавайте Issues в репозитории.
