#!/bin/bash

PURPLE='\033[0;35m'
NO_COLOR='\033[0m'

cd SkyLibrary

echo "${PURPLE}Collect static files${NO_COLOR}"
python manage.py collectstatic --noinput --clear

echo "${PURPLE}Apply database migrations${NO_COLOR}"
python manage.py migrate --noinput

echo "${PURPLE}Create cache table${NO_COLOR}"
python manage.py createcachetable

echo "${PURPLE}Compile translate messages${NO_COLOR}"
python manage.py compilemessages

echo "${PURPLE}Run tests${NO_COLOR}"
python manage.py test --noinput

echo "${PURPLE}Run server${NO_COLOR}"
gunicorn app_main.wsgi:application --workers 3 --timeout 60 --bind 0.0.0.0:8000
