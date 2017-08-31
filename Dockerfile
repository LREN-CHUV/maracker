FROM python:3.6

WORKDIR /var/www/maracker/

EXPOSE 8000

COPY maracker .
COPY entrypoint.sh .

RUN pip install -r requirements.txt && \
    pip install uwsgi && \
    python manage.py collectstatic --no-input

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]

# CMD ["uwsgi", "--http", ":8000", "--wsgi-file", "maracker/wsgi.py", \
#     "--static-map", \
#     "/static/=/var/www/maracker/static" \
# ]
