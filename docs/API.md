# API oversikt

Base path: `/api/v1`

## Auth

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

## Generatorer

- `GET /generators`

## Moduser

- `POST /modes/exam/start`
- `POST /modes/training/start`
- `POST /modes/training/{session_id}/next`
- `POST /modes/sessions/{session_id}/submit`
- `GET /modes/sessions/{session_id}/summary`

## Progresjon

- `GET /progress/me/overview`
- `GET /progress/me/per-generator`
- `GET /progress/me/timeline`

## Admin / Dev

- `GET /admin/generators`
- `PATCH /admin/generators/{key}`
- `GET /admin/generators/{key}/sample`
- `POST /admin/generators/{key}/stress?count=1000`

## Interaktiv dokumentasjon

Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`
