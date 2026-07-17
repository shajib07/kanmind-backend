# Kanmind Backend

Django REST Framework backend for the Kanmind course project.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv env
source env/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The API is available under:

```text
http://127.0.0.1:8000/api/
```

## Authentication

Authenticated requests must include a token header:

```text
Authorization: Token <your-token>
```

Current authentication endpoints:

```text
POST /api/registration/
POST /api/login/
GET  /api/email-check/?email=user@example.com
```

## Repository Notes

This repository contains only the backend. The local SQLite database,
virtual environment, coverage reports, environment files, and IDE settings
are ignored by git.
