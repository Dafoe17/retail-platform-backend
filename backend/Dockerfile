FROM python:3.11-slim

WORKDIR /app

# Установить зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать код
COPY . .

# Запустить (Render устанавливает PORT автоматически)
CMD ["uvicorn", "core.app:app", "--host", "0.0.0.0", "--port", "$PORT"]
