# BabyCare AI Platform

Monorepo starter for an AI-assisted baby care application.

## Structure

- `client/` — React, TypeScript, Vite, and Tailwind CSS
- `server/` — FastAPI on Python 3.11
- `shared/types/` — TypeScript interfaces and mirrored Pydantic models

## Quick start

1. Copy `.env.example` to `.env` and fill in any required values.
2. Install dependencies:
   - `npm install`
   - `python3.11 -m venv .venv && .venv/bin/pip install -e "server[dev]"`
3. Run `make dev`.

The client runs at <http://localhost:5173>, the API at
<http://localhost:8000>, and Postgres at `localhost:5432`.

| Client | Server |
| --- | --- |
| React + TypeScript | FastAPI + Python 3.11 |
| `http://localhost:5173` | `http://localhost:8000` |
| `npm --workspace @babycare/client run dev` | `.venv/bin/uvicorn app.main:app --app-dir server --reload` |

The root `.gitignore` keeps generated client and server files out of version
control while retaining `.env.example` as the shared configuration template.

## Commands

- `make dev` — start Postgres, the API, and the Vite development server
- `make test` — run client and server checks/tests
- `make seed` — insert local development seed data

## Database migrations

Create a migration after changing models:

```bash
.venv/bin/alembic -c server/alembic.ini revision --autogenerate -m "describe change"
```

Apply migrations with:

```bash
.venv/bin/alembic -c server/alembic.ini upgrade head
```
