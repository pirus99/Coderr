# Coderr
Coderr Django Backend Project - DA

Django backend for Coderr Frontend.

## Prerequisites

- Python 3.10+ (project used 3.13 on this machine)
- Git
- Windows (commands below use Windows CMD / PowerShell)

## Environment Configuration

For production deployment, create a `.env` file in the project root or set environment variables:

- `DJANGO_SECRET_KEY` - Secret key for Django (generate a new one for production)
- `DJANGO_DEBUG` - Set to `False` in production (default: `True`)
- `DJANGO_ALLOWED_HOSTS` - Comma-separated list of allowed hosts (e.g., `yourdomain.com,www.yourdomain.com`)

See `.env.example` for a template.

To generate a new secret key:
```python
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## Quick setup (development)

1. Create and activate virtualenv
   - CMD:
     ```
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - PowerShell:
     ```
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```
   If requirements.txt is missing, install the basics:
   ```
   pip install django djangorestframework djangorestframework-authtoken pytest pytest-django
   ```

3. Configure environment (optional for one-off run)
   ```
   set DJANGO_SETTINGS_MODULE=core.settings
   ```

4. Database migrations
   ```
   python manage.py migrate
   ```

5. Create superuser
   ```
   python manage.py createsuperuser
   ```

6. Run development server
   ```
   python manage.py runserver
   ```

## Running tests

- Ensure pytest-django is installed and pytest.ini contains:
  ```
  [pytest]
  DJANGO_SETTINGS_MODULE = core.settings
  python_files = tests.py test_*.py *_tests.py
  ```
- Run tests:
  ```
  pytest -q
  ```

## Notes

- REST framework uses TokenAuthentication by default (see core/settings.py).
- Rate limiting is configured (100 requests/hour for anonymous, 1000 requests/hour for authenticated users).
- For production:
  - Set `DEBUG=False` via `DJANGO_DEBUG=False` environment variable
  - Configure `ALLOWED_HOSTS` via `DJANGO_ALLOWED_HOSTS` environment variable
  - Generate and set a new `SECRET_KEY` via `DJANGO_SECRET_KEY` environment variable
  - Use a production-ready database (PostgreSQL recommended) instead of SQLite
  - Configure a web server (nginx/Apache) and WSGI server (Gunicorn/uWSGI)
  - Set up HTTPS/SSL certificates
- Collect static files for production:
  ```
  python manage.py collectstatic --noinput
  ```
- File uploads are limited to 5MB by default
- Allowed file extensions: jpg, jpeg, png, pdf, doc, docx