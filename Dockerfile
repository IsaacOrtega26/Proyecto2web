FROM python:3.12-slim

WORKDIR /app

# Copiar requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Comando por defecto (lo sobreescribimos en docker-compose)
CMD ["python", "api/json_api_server.py"]
