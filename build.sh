#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
# I forced prod settings here so collectstatic/migrate don't accidentally use dev config on Render.
python manage.py collectstatic --noinput --settings=zeecommerce.settings.prod
python manage.py migrate --settings=zeecommerce.settings.prod
