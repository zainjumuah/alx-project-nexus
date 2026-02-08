# ZeeCommerce API

Production-ready e-commerce backend API built with Django + DRF.

This project provides product and category management with JWT authentication, discovery filters, pagination, Swagger docs, and deployment-ready settings for Render.

## Live URLs

- Base URL: `https://zeecommerce-api.onrender.com`
- Swagger UI: `https://zeecommerce-api.onrender.com/swagger/`
- ReDoc: `https://zeecommerce-api.onrender.com/redoc/`

## Core Features

- Products CRUD: `/api/products/`, `/api/products/<id>/`
- Categories CRUD: `/api/categories/`, `/api/categories/<id>/`
- JWT auth flow:
  - Register: `/api/auth/register/`
  - Obtain token: `/api/auth/token/`
  - Refresh token: `/api/auth/token/refresh/`
  - Verify token: `/api/auth/token/verify/`
- Product discovery:
  - Filter by category: `?category=<id>`
  - Ordering: `?ordering=price`, `?ordering=-price`, `?ordering=created_at`, `?ordering=-created_at`
  - Pagination: `?page=<n>&page_size=<n>`
- API docs grouped by tags: Products, Categories, Auth
- Performance guardrails with query-count tests

## Tech Stack

- Python 3.12+
- Django 5.x
- Django REST Framework
- PostgreSQL
- `djangorestframework-simplejwt`
- `drf-yasg` (Swagger/OpenAPI)
- WhiteNoise (static files in production)

## Local Setup

### 1) Clone and enter project

```bash
git clone <YOUR_REPO_URL>
cd alx-project-nexus
```

### 2) Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

```bash
cp .env.example .env
```

Expected keys (from `.env.example`):

```env
SECRET_KEY=put-yours-here
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_SETTINGS_MODULE=zeecommerce.settings.dev
```

### 5) Migrate and run

```bash
python manage.py migrate
python manage.py runserver
```

Local API: `http://127.0.0.1:8000`

## Auth Flow (curl)

```bash
export BASE_URL="http://127.0.0.1:8000"
# export BASE_URL="https://zeecommerce-api.onrender.com"
```

### Register

```bash
curl -i -X POST "$BASE_URL/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","email":"demo_user@example.com","password":"StrongPass123!"}'
```

### Obtain JWT

```bash
curl -s -X POST "$BASE_URL/api/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"StrongPass123!"}'
```

Save tokens from response:

```bash
export TOKEN="<access_token>"
export REFRESH="<refresh_token>"
```

### Refresh

```bash
curl -i -X POST "$BASE_URL/api/auth/token/refresh/" \
  -H "Content-Type: application/json" \
  -d '{"refresh":"'$REFRESH'"}'
```

### Verify

```bash
curl -i -X POST "$BASE_URL/api/auth/token/verify/" \
  -H "Content-Type: application/json" \
  -d '{"token":"'$TOKEN'"}'
```

## API Usage Examples

### List products (public)

```bash
curl -i "$BASE_URL/api/products/"
```

### Create category (auth required)

```bash
curl -i -X POST "$BASE_URL/api/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Phones","slug":"phones"}'
```

### Create product (auth required)

```bash
curl -i -X POST "$BASE_URL/api/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Deployed Test","description":"Demo item","price":"10.00","stock":1,"category":1}'
```

### Discovery query

```bash
curl -i "$BASE_URL/api/products/?category=1&ordering=price&page=1&page_size=10"
```

## Tests

Run the full test suite:

```bash
python manage.py test
```

## Deployment (Render)

This repo is configured for Render Blueprint deployment (`render.yaml` + `build.sh`).

Build script runs:

- `pip install -r requirements.txt`
- `python manage.py collectstatic --noinput --settings=zeecommerce.settings.prod`
- `python manage.py migrate --settings=zeecommerce.settings.prod`

Production runtime uses:

- `DJANGO_SETTINGS_MODULE=zeecommerce.settings.prod`
- `WhiteNoise` static handling
- hardened host/proxy settings

## Common Gotchas

- DRF routers enforce trailing slashes:
  - Use `/api/products/` not `/api/products`
- Token obtain expects `username` + `password` keys
- Creating a product requires a valid existing `category` id
- If auth works in Swagger but fails in curl, verify header format:
  - `Authorization: Bearer <access_token>`

## Project Structure (high level)

```text
zeecommerce/         # project config + settings
products/            # product/category models, serializers, viewsets, tests
users/               # registration + JWT docs wrappers + auth routes
common/              # shared utilities (pagination)
```
