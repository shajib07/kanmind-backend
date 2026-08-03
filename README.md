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

## API Endpoints

### Authentication

```text
POST /api/registration/
POST /api/login/
GET  /api/email-check/?email=user@example.com
```

### Boards

```text
GET    /api/boards/
POST   /api/boards/
GET    /api/boards/{board_id}/
PATCH  /api/boards/{board_id}/
DELETE /api/boards/{board_id}/
```

### Tasks

```text
GET    /api/tasks/assigned-to-me/
GET    /api/tasks/reviewing/
POST   /api/tasks/
PATCH  /api/tasks/{task_id}/
DELETE /api/tasks/{task_id}/
```

### Comments

```text
GET    /api/tasks/{task_id}/comments/
POST   /api/tasks/{task_id}/comments/
DELETE /api/tasks/{task_id}/comments/{comment_id}/
```

## Permissions

- All board, task, comment and email-check endpoints require token authentication.
- Board owners and members can view and update their boards.
- Only a board owner can delete a board.
- Board members can create and update tasks.
- Only the task creator or board owner can delete a task.
- Board members can list and create comments.
- Only the comment author can delete a comment.
- Task assignees and reviewers must be members of the corresponding board.

## Repository Notes

This repository contains only the backend. The local SQLite database,
virtual environment, coverage reports, environment files, and IDE settings
are ignored by git.
