# Imagem base Python
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 

WORKDIR /app

# Instala bibliotecas diretamente (sem requirements.txt)
RUN pip install --upgrade pip && pip install \
    fastapi==0.116.1 \
    uvicorn[standard]==0.35 \
    orjson==3.11.3 \
    gunicorn==23.0.0 \
    pymongo==4.14.1 \
    redis==6.4.0 \ 
    opentelemetry-distro==0.57b0 \
    opentelemetry-instrumentation==0.57b0 \
    opentelemetry-exporter-otlp==1.36.0 \
    opentelemetry-instrumentation-fastapi==0.57b0 \
    opentelemetry-instrumentation-pymongo==0.57b0 \
    opentelemetry-instrumentation-redis==0.57b0 \
    prometheus-fastapi-instrumentator==7.1.0        

# Copia o app
COPY main.py .

EXPOSE 8000

ENTRYPOINT ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "-w", "3", "--log-level", "warning", "--preload", "--reuse-port", "--worker-connections", "1000"]
# ENTRYPOINT ["granian",  "--interface",  "asginl",  "main_puro:app", "--host", "0.0.0.0", "--port", "8000", "--no-log", "--no-ws", "--loop", "uvloop", "--backlog", "16000", "--backpressure", "1000", "--task-impl", "asyncio", "--workers", "1"]