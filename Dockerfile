FROM python:3.12-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install --yes --no-install-recommends \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar archivos de aplicación
COPY requirements.txt .
COPY main.py .
COPY voices/ ./voices/

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
