# E-Commerce Backend (Django + DRF)

Backend API for an e-commerce product catalog built with Django and Django REST Framework.

This project is designed as a **real-world backend system**, not a toy app.
It emphasizes clean architecture, PostgreSQL usage, disciplined version control, and API readiness for frontend consumption.

## Tech Stack

- Python 3.12+
- Django + Django REST Framework
- PostgreSQL
- Redis (later: caching, Celery)
- JWT Authentication (planned)
- Swagger / OpenAPI (planned)

## Requirements

- Python 3.12 or higher
- PostgreSQL installed and running
- Redis (optional for later stages)

## Local Development Setup

### 1) Clone the repository

```bash
git clone <REPO_URL>
cd alx-project-nexus
```

### 2) Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Environment configuration

Create your local environment file:

```bash
cp .env.example .env
```

Edit `.env` and set values exactly as required:

```bash
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_SETTINGS_MODULE=zeecommerce.settings.dev
```

Notes:

- `.env` must never be committed.
- `DATABASE_URL` must point to an existing PostgreSQL database.
- For local development, `DJANGO_SETTINGS_MODULE` should be `zeecommerce.settings.dev`.

### 5) PostgreSQL setup (example)

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE dbname;
CREATE USER user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE dbname TO user;
```

Ensure the credentials match your `DATABASE_URL`.

### 6) Database migrations and server

```bash
python manage.py migrate
python manage.py runserver
```

Server will be available at:
`http://127.0.0.1:8000/`

## Useful Commands

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
python manage.py test
```

## Project Status

Known limitation (acknowledged):

- `python manage.py check` may fail if the admin is configured to filter on a `Product.category` field before the `Product → Category` relationship is implemented (or updated).
- This is a known, intentional state and will be resolved in the next development cycle.

## Version Control Discipline

- `.env` and local DB files are ignored.
- `.env.example` is the single source of truth for environment configuration.
- Commits should be descriptive and intentional.
