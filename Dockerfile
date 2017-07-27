FROM python:3.6

WORKDIR /var/www/maracker/

EXPOSE 8000

COPY maracker .

RUN pip install -r requirements.txt && \
    pip install uwsgi

CMD ["uwsgi", "--http", ":8000", "--wsgi-file", "maracker/wsgi.py"]
