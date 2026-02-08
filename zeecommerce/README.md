# ZeeCommerce Project Config

`zeecommerce` is the Django project package. It owns root routing, environment-specific settings, and runtime entrypoints (WSGI/ASGI).

## Responsibilities

- Root URL routing (`/api/`, `/api/auth/`, `/swagger/`, `/redoc/`)
- Base/dev/prod settings split
- Deployment-safe security/static/runtime configuration
- WSGI/ASGI boot configuration

## Key Files

- `zeecommerce/urls.py`: project-level route map + Swagger schema view
- `zeecommerce/settings/base.py`: shared settings
- `zeecommerce/settings/dev.py`: local development overrides
- `zeecommerce/settings/prod.py`: production hardening
- `zeecommerce/wsgi.py`: Gunicorn/WSGI entrypoint
- `zeecommerce/asgi.py`: ASGI entrypoint

## Settings Notes

- Local default: `zeecommerce.settings.dev` (via `manage.py`)
- Production runtime: `zeecommerce.settings.prod` (Render env var)
- Static in prod uses WhiteNoise with `STATIC_ROOT` and manifest storage

## Deployment Notes

- `render.yaml` + `build.sh` are aligned to production settings.
- Build uses prod settings for `collectstatic` and `migrate`.
- Keep `ALLOWED_HOSTS` strict in production; no wildcard `*`.
