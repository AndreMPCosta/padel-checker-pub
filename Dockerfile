FROM python:3.9.8

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV WORKDIR=/usr/padel
ENV USER=padel
ENV APP_HOME=/home/padel/padel-checker


RUN pip install --upgrade pip
RUN pip install pipenv

RUN adduser --system --group $USER
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

COPY . $APP_HOME
RUN chown -R $USER:$USER $APP_HOME
USER $USER

RUN pipenv install