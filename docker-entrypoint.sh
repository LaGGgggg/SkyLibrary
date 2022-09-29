#!/bin/bash

PURPLE='\033[0;35m'
NO_COLOR='\033[0m'

cd SkyLibrary

echo "${PURPLE}Collect static files${NO_COLOR}"
python manage.py collectstatic --noinput

echo "${PURPLE}Apply database migrations${NO_COLOR}"
python manage.py migrate

echo "${PURPLE}Create cache table${NO_COLOR}"
python manage.py createcachetable

echo "${PURPLE}Compile translate messages${NO_COLOR}"
python manage.py compilemessages

echo "${PURPLE}Run tests${NO_COLOR}"
python manage.py test

echo "${PURPLE}Run development server${NO_COLOR}"
python manage.py runserver 0.0.0.0:8000