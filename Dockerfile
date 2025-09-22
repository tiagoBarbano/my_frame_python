FROM python:3.13.7-slim AS base

# Evita criar .pyc e melhora logs em containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LC_ALL=C.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    TERM=screen

# Diretório da aplicação
WORKDIR /app

# Copia apenas o requirements primeiro para aproveitar cache de build
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip certifi \
    && pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY main.py .
COPY app ./app

# Diretório para métricas (com permissões corretas)
RUN mkdir -p /app/metrics \
    && chown -R nobody:nogroup /app
USER nobody

EXPOSE 8000

CMD ["python", "main.py"]
