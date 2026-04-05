FROM python:3.12-alpine
LABEL maintainer="Konstantin-SVT"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

RUN mkdir -p vol/media
RUN mkdir -p staticfiles
RUN mkdir -p fixtures

RUN adduser --no-create-home --disabled-password django-user
RUN chown -R django-user vol
RUN chmod -R 755 vol
RUN chown -R django-user staticfiles
RUN chmod -R 755 staticfiles

USER django-user

CMD sh -c "python manage.py collectstatic --noinput && \
           python manage.py wait_for_db && \
           python manage.py migrate && \
           daphne -b 0.0.0.0 -p $PORT catalogue_system.settings:ASGI_APPLICATION"