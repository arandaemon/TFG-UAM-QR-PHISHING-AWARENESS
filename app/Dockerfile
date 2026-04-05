# Usamos una versión ligera y estable
FROM python:3.11-slim

# Evita que Python genere archivos .pyc y permite logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalación de dependencias (Aprovechando el caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear un usuario no privilegiado (CWE-250)
# Por defecto Docker corre como root. Si un atacante escapa del proceso Flask, 
# tendría control total del contenedor. Con un usuario "appuser" limitamos el daño.
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Copiamos el código (después de crear el usuario para mantener permisos)
COPY . .

# Puerto de Gunicorn
EXPOSE 8000

# Comando de ejecución optimizado
CMD ["gunicorn", \
     "--workers", "4", \
     "--threads", "2", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "main:app"]