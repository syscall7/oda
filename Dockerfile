FROM ubuntu:bionic-20190204
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    openssh-server \
    python3-pip \
    postgresql-client \
    libmysqlclient-dev \
    libxml2-dev \
    libxslt1-dev \
    binutils-multiarch \
    binutils-multiarch-dev

RUN mkdir /code
WORKDIR /code
COPY django/requirements.txt /code/django/
RUN pip3 install gunicorn && pip3 install -r /code/django/requirements.txt

run mkdir /var/oda
RUN mkdir /var/oda/cache

COPY . /code/


