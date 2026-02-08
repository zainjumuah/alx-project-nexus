"""
ASGI config for zeecommerce project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# I keep this aligned with wsgi so deploy/runtime entrypoints behave the same way.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zeecommerce.settings.prod")

application = get_asgi_application()
