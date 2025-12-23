# Coderr
Coderr Django Backend Project - DA

Django backend for Coderr Frontend.

## Prerequisites

- Python 3.10+ (project used 3.13 on this machine)
- Git
- Windows (commands below use Windows CMD / PowerShell)

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
   (you can run the Project without these setting, default values given in settings.py will be used then.)
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
- For production set DEBUG=False, configure ALLOWED_HOSTS and a proper SECRET_KEY.
- Collect static files for production:
  ```
  python manage.py collectstatic --noinput
  ```