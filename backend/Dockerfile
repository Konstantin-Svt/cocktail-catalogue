FROM python:3.12-alpine
LABEL maintainer="Konstantin-SVT"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

RUN mkdir -p vol/media
RUN mkdir -p fixtures

RUN adduser --no-create-home --disabled-password django-user
RUN chown -R django-user vol
RUN chmod -R 755 vol

USER django-user

EXPOSE 8000

CMD python manage.py wait_for_db && python manage.py migrate && gunicorn --access-logfile - --error-logfile - --bind 0.0.0.0:8000 catalogue_system.wsgi