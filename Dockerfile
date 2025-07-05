FROM python:3.10-slim

WORKDIR /app

# Instala dependencias del sistema si es necesario
# RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear usuario no root (opcional)
# RUN useradd -m appuser
# USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
