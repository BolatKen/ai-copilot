# Dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=backend.settings

# Установка рабочей директории
WORKDIR /app

# Копирование requirements.txt
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt


# Создание пользователя и подготовка директорий/прав
RUN adduser --disabled-password --gecos '' appuser \
    && mkdir -p /app/media /app/logs /app/staticfiles \
    && touch /app/logs/ai_copilot.log \
    && chown -R appuser:appuser /app

# Копирование кода приложения (после создания пользователя и директорий)
COPY . .

USER appuser

# Открытие порта
EXPOSE 8005

# Команда запуска
CMD ["gunicorn", "--bind", "0.0.0.0:8005", "--workers", "3", "--timeout", "120", "backend.wsgi:application"]
