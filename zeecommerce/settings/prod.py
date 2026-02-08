from .base import *
from django.core.exceptions import ImproperlyConfigured

DEBUG = False #prod environment

if not ALLOWED_HOSTS or ALLOWED_HOSTS == ["127.0.0.1", "localhost"]:
    raise ImproperlyConfigured("ALLOWED_HOSTS must be set in production, dear.")

# I set this so collectstatic has one clear output directory in production.
STATIC_ROOT = BASE_DIR / "staticfiles"

# I use WhiteNoise storage in prod so static assets are compressed and cache-friendly.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

#defaults for now, I'll tweak them later
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

"""
SECURE_HSTS_SECONDS = 31536000 
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
"""
