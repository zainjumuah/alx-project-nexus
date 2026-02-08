import os
from pathlib import Path
import environ
from django.core.exceptions import ImproperlyConfigured

# I'm stepping three levels up because this file sits inside `zeecommerce/settings/` now.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

# I only load `.env` in dev settings so production uses real platform env vars only.
ENV_FILE = BASE_DIR / ".env"
settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "")
if settings_module.endswith(".dev") and ENV_FILE.exists():
    environ.Env.read_env(str(ENV_FILE))

def require(var_name: str) -> str:
    """I fail fast when a required environment variable is missing."""
    try:
        return env(var_name)
    except Exception as exc:
        raise ImproperlyConfigured(
            f"Missing required env: {var_name}"
        ) from exc

# I'll keep sensitive values in ens only.
SECRET_KEY = require("SECRET_KEY")
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# App defs
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_filters",

    # Third-party apps
    "rest_framework",
    "drf_yasg",

    # Local apps
    "products",
    "users",

    # Auth
    "rest_framework_simplejwt",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # I kept this right after SecurityMiddleware so static files are served efficiently in prod.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "zeecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "zeecommerce.wsgi.application"


# Database
DATABASES = {"default": env.db("DATABASE_URL")}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# i18n
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True


# Static
# I used a full slash path so static URLs are unambiguous (I just learned this, haha) across environments.
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# DRF defaults
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticatedOrReadOnly",),
    # I switched to our custom paginator so `page_size` query param is supported safely.
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardResultsSetPagination",
    # I set this to match the paginator default so behavior is predictable in tests/docs.
    "PAGE_SIZE": 10,
}


SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    # I kept auth persisted in Swagger so I don't have to paste tokens repeatedly while testing.
    "PERSIST_AUTH": True,
    "DISPLAY_OPERATION_ID": False,
    "SECURITY_DEFINITIONS": {
        "Bearer (JWT)": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Paste: Bearer <access_token>",
        }
    },
    # I set this so protected endpoints visibly show auth requirement in Swagger UI.
    "SECURITY_REQUIREMENTS": [{"Bearer (JWT)": []}],
}

AUTH_USER_MODEL = 'users.CustomUser'
