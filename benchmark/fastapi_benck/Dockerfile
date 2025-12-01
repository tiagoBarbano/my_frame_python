# Imagem base Python
FROM python:3.13.7-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 

WORKDIR /app

# Instala bibliotecas diretamente (sem requirements.txt)
RUN pip install --upgrade pip && pip install \
    fastapi==0.116.1 \
    granian[uvloop]==2.5.4 \
    uvloop==0.21.0 \
    uvicorn[standard]==0.35 \
    orjson==3.11.3 \
    gunicorn==23.0.0 \
    pymongo==4.14.1 \
    redis==6.4.0 \ 
    msgspec==0.19.0   

# Copia o app
COPY main.py .

EXPOSE 8000

ENTRYPOINT [ "sh", "-c", "\
    exec gunicorn main:app \
        -k uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --workers 1 \
        --worker-connections 75000 \
        --keep-alive 2 \
        --timeout 30 \
        --graceful-timeout 5 \
        --log-level warning \
        --preload \
        --reuse-port" ]

# ENTRYPOINT [ "sh", "-c", "\
#     exec granian \
#         --interface asgi \
#         --host 0.0.0.0 \
#         --port 8000 \
#         --workers 1 \
#         main:app" ]