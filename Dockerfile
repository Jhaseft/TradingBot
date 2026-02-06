#  Imagen base Python
FROM python:3.10-slim

#  Variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#  Crear directorio de la app
WORKDIR /app

# Copiar requirements y luego instalar (para cachear mejor)
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#  Copiar todo el proyecto
COPY . .

#  Exponer puerto
EXPOSE 8000

#  Comando por defecto al arrancar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
