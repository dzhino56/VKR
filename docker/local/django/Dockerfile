FROM python:3.7-slim-buster

ENV APP_HOME=/app
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

LABEL maintainer='e.pavlov98@mail.ru'

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y libpq-dev
RUN apt-get install -y gettext
RUN apt-get -y install netcat gcc postgresql
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false
RUN rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY ./docker/local/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

ENTRYPOINT [ "/entrypoint"]