"""
WSGI config for zeecommerce project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# I default to prod here so deployment doesn't silently boot with dev settings.
# Local dev commands still use manage.py, so this won't block normal local workflow.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zeecommerce.settings.prod")

application = get_wsgi_application()
