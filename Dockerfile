FROM python:3.6

RUN mkdir -p /var/www/maracker
COPY . /var/www/maracker
WORKDIR /var/www/maracker
