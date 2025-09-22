# Imagem base Python
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    OTEL_RESOURCE_ATTRIBUTES=service.name=fastapi-otel-svc \
    OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317 \
    OTEL_TRACES_SAMPLER=parentbased_always_on

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala bibliotecas diretamente (sem requirements.txt)
RUN pip install --upgrade pip && pip install \
    fastapi==0.116.1 \
    uvicorn[standard]==0.35 \
    gunicorn==23.0.0 \    
    orjson==3.11.3 \
    pymongo==4.14.1 \
    redis==6.4.0 \    
    opentelemetry-distro==0.57b0 \
    opentelemetry-instrumentation==0.57b0 \
    opentelemetry-exporter-otlp==1.36.0 \
    opentelemetry-instrumentation-fastapi==0.57b0 \
    opentelemetry-instrumentation-pymongo==0.57b0 \
    opentelemetry-instrumentation-redis==0.57b0 \
    opentelemetry-instrumentation-asgi==0.57b0 

# Copia o app
COPY main.py .

EXPOSE 8000

# Usa auto-instrumentação do OpenTelemetry com Uvicorn
ENTRYPOINT ["opentelemetry-instrument", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning", "--workers", "4"]

