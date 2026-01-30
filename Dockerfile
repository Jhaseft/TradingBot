# 1️⃣ Imagen base Python
FROM python:3.10-slim

# 2️⃣ Variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3️⃣ Crear directorio de la app
WORKDIR /app

# 4️⃣ Copiar requirements y luego instalar (para cachear mejor)
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 5️⃣ Copiar todo el proyecto
COPY . .

# 6️⃣ Exponer puerto
EXPOSE 8000

# 7️⃣ Comando por defecto al arrancar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
