FROM python:3.13.3-slim
RUN mkdir src

# ENV PROMETHEUS_MULTIPROC_DIR="metrics"
ENV APP_NAME="MY_FRAME_GRANIAN"
ENV LOGGER_LEVEL="info"
ENV LC_ALL=C.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV TERM=screen

COPY requirements.txt src
COPY app.py src
COPY main.py src
COPY config.py src
COPY logger.py src
COPY metrics.py src
COPY routing.py src
COPY tracing.py src

WORKDIR /src
RUN mkdir metrics
RUN pip install --no-cache-dir --upgrade certifi
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8000
CMD ["granian", "main:app", "--interface", "asginl", "--host", "0.0.0.0", "--port", "8000"]