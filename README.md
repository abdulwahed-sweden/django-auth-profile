# AuthProfile

A Django starter with authentication, user profiles, and a REST API.

Built with Django 5.2, Django REST Framework, and Bootstrap 5.

## Quick Start

```bash
git clone https://github.com/abdulwahed-sweden/django-auth-profile.git
cd django-auth-profile

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env      # edit SECRET_KEY
python manage.py migrate
python manage.py seed_users
python manage.py runserver
```

Open http://127.0.0.1:8000

## Test Accounts

| Username | Password | Role |
|---|---|---|
| `admin` | `Admin123!` | Superuser |
| `erik.lindberg` | `SwedishTest123!` | User |
| `anna.johansson` | `SwedishTest123!` | User |
| `oscar.nilsson` | `SwedishTest123!` | User |
| `sara.eriksson` | `SwedishTest123!` | User |
| `karl.svensson` | `SwedishTest123!` | User |

## Pages

| URL | Description | Auth |
|---|---|---|
| `/` | Home | No |
| `/register/` | Create account | No |
| `/login/` | Sign in | No |
| `/dashboard/` | User dashboard | Yes |
| `/profile/` | Edit profile | Yes |
| `/password-change/` | Change password | Yes |
| `/password-reset/` | Forgot password | No |
| `/about/` | About | No |
| `/help/` | Help center | No |
| `/admin/` | Admin panel | Staff |

## API Endpoints

All API endpoints require authentication (session or token).

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/profiles/` | List all profiles |
| `POST` | `/api/profiles/` | Create a profile |
| `GET/PUT/PATCH/DELETE` | `/api/profiles/{id}/` | Profile detail |
| `GET` | `/api/users/` | List users (read-only) |
| `GET` | `/api/users/{id}/` | User detail (read-only) |

**API docs:** `/api/docs/` (Swagger) | `/api/redoc/` (ReDoc) | `/api/schema/` (OpenAPI JSON)

```bash
# Token auth
curl -H "Authorization: Token YOUR_TOKEN" http://127.0.0.1:8000/api/profiles/
```

## Tech Stack

Django 5.2 | DRF 3.16 | Bootstrap 5.3 | drf-spectacular | SQLite | WhiteNoise | Gunicorn

## License

MIT
