# Dockerfile
FROM python:3.12-slim

# Evita que Python genere archivos .pyc y buffer de salida
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# El comando por defecto (se sobrescribe en docker-compose, pero es buena práctica)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]