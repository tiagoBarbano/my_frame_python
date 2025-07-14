FROM python:3.13.5-slim
RUN mkdir src

ENV LC_ALL=C.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV TERM=screen

COPY requirements.txt src
COPY main.py src
COPY app src/app

WORKDIR /src
RUN mkdir metrics
RUN pip install --no-cache-dir --upgrade certifi
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8000
CMD ["python", "main.py"]