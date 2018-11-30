#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset


#python /app/manage.py runserver --noinput
gunicorn haiyi.wsgi -w 1 -b 0.0.0.0:8000 --chdir=/app
#gunicorn --chdir /haiyi --bind :5000 haiyi.wsgi:application
