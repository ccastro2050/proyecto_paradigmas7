# Dockerfile del FRONT — Flask + Jinja2, puerto 8023.
#
# Es una imagen aparte de la de la API, y eso no es un capricho: son dos
# procesos distintos, con dependencias distintas, que se despliegan y se
# reinician por separado. La separación de capas de la v5 empieza aquí.
FROM python:3.12-slim

WORKDIR /app

# Primero las dependencias y después el código: así, mientras requirements.txt
# no cambie, Docker reutiliza la capa del pip install y reconstruir es rápido.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PUERTO=8023
EXPOSE 8023

CMD ["python", "app.py"]
