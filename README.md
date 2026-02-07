# Django Auth Profile

A Django project with user authentication, profiles, and a REST API.

## Tech Stack

- Django 5.2
- Django REST Framework 3.16
- Bootstrap 5 (via django-bootstrap5)
- SQLite

## Quick Start

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Run migrations
python manage.py migrate

# Seed sample data
python manage.py seed_users

# Start server
python manage.py runserver
```

Open http://127.0.0.1:8000

## Test Accounts

| Username | Password | Role |
|---|---|---|
| admin | Admin123! | Superuser |
| erik.lindberg | SwedishTest123! | User (Stockholm) |
| anna.johansson | SwedishTest123! | User (Gothenburg) |
| oscar.nilsson | SwedishTest123! | User (Malmö) |
| sara.eriksson | SwedishTest123! | User (Uppsala) |
| karl.svensson | SwedishTest123! | User (Linköping) |

## URLs

| URL | Description |
|---|---|
| / | Dashboard (login required) |
| /login/ | Login page |
| /register/ | Registration page |
| /profile/ | Edit profile |
| /api/ | Browsable API root |
| /api/profiles/ | Profiles CRUD |
| /api/users/ | Users list (read-only) |
| /admin/ | Django admin |

## Project Structure

```
├── config/          # Django project settings
├── apps/accounts/   # Auth, profiles, API
├── templates/       # HTML templates
├── static/css/      # Custom styles
├── manage.py
└── requirements.txt
```
