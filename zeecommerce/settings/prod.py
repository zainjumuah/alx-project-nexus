from .base import *
from django.core.exceptions import ImproperlyConfigured

DEBUG = False  # Production environment

# this will append Render's external hostname automatically so production host validation stays tight.
render_external_hostname = env("RENDER_EXTERNAL_HOSTNAME", default="")
if render_external_hostname and render_external_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_external_hostname)

# and this one will block wildcards in prod so host validation cannot be bypassed.
if "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("Wildcard '*' is not allowed in ALLOWED_HOSTS for production.")

if not ALLOWED_HOSTS or set(ALLOWED_HOSTS).issubset({"127.0.0.1", "localhost"}):
    raise ImproperlyConfigured("ALLOWED_HOSTS must be set in production, dear.")

# I set this so collectstatic has one clear output directory in prod.
STATIC_ROOT = BASE_DIR / "staticfiles"

# I use WhiteNoise storage in prod so static assets are compressed and cache-friendly.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
# I set this to avoid hard-fail on missing sourcemap refs from third-party static assets.
WHITENOISE_MANIFEST_STRICT = False

# I kept proxy/SSL flags explicit so request scheme + host are correct behind Render.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# I trust (fully o) forwarded host from the proxy so Swagger "Try it out" builds https URLs correctly.
USE_X_FORWARDED_HOST = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
