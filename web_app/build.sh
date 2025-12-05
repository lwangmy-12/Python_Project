#!/usr/bin/env bash
# exit on error
set -o errexit

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py import_bridges
