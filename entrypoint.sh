#!/bin/bash

uwsgi --http :8000 --wsgi-file maracker/wsgi.py \
    --static-map /static/=/var/www/maracker/static
