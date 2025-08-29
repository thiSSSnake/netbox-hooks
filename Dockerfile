# Используем официальный образ Python как базовый
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Открываем порт, на котором будет работать Uvicorn
EXPOSE 8080

# Запускаем Uvicorn для вашего приложения
# Убедитесь, что путь к вашему главному файлу (main.py) правильный
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]