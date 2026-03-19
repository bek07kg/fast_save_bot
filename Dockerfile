# Используем легкий образ Python
FROM python:3.11-slim

# Устанавливаем ffmpeg прямо внутри контейнера
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Создаем рабочую папку
WORKDIR /app

# Копируем список зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем папку для загрузок
RUN mkdir -p downloads

# Команда для запуска
CMD ["python", "bot.py"]
