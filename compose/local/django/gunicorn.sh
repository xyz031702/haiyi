#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset


python manage.py collectstatic
python /app/manage.py migrate
gunicorn haiyi.wsgi -w 1 -b 0.0.0.0:8000 --chdir=/app
#gunicorn --chdir /haiyi --bind :5000 haiyi.wsgi:application
