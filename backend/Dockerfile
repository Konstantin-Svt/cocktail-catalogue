FROM python:3.12-alpine
LABEL maintainer="Konstantin-SVT"

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip
COPY backend/requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY backend/ /app/

RUN mkdir -p vol/media
RUN mkdir -p fixtures

RUN adduser --no-create-home --disabled-password django-user
RUN chown -R django-user vol
RUN chmod -R 755 vol

USER django-user