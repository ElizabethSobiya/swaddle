# Swaddle

Monorepo starter for an AI-assisted baby care application.

## Structure

- `client/` — React, TypeScript, Vite, and Tailwind CSS
- `server/` — FastAPI on Python 3.11
- `shared/types/` — TypeScript interfaces and mirrored Pydantic models

## Quick start

### Prerequisites

- Node.js 20 or newer and npm
- Python 3.11
- Docker Desktop (running)
- Tesseract OCR (only required for prescription image/PDF extraction)

### Install and run

Run these commands from the repository root:

```bash
# 1. Install the client and server dependencies.
make install

# 2. Create your local configuration.
cp .env.example .env

# 3. Start Postgres (the Compose service is named "db").
docker compose up -d db

# 4. Apply migrations and load the resettable demo data.
make seed

# 5. Start both the FastAPI and Vite development servers.
make dev
```

Set `OPENAI_API_KEY` in `.env` to use symptom checking, prescription
structuring, and optional product AI explanations. The age-based product and
content browsing flows work without it. `CLOUDINARY_URL` is only a placeholder
for roadmap storage integration and is not required by this version.

The client runs at <http://localhost:5173>, the API at
<http://localhost:8001>, and Postgres at `localhost:5433` (mapped to port 5432
inside Docker).

| Client | Server |
| --- | --- |
| React + TypeScript | FastAPI + Python 3.11 |
| `http://localhost:5173` | `http://localhost:8001` |
| `npm --workspace @swaddle/client run dev` | `.venv/bin/uvicorn app.main:app --app-dir server --reload --port 8001` |

The root `.gitignore` keeps generated client and server files out of version
control while retaining `.env.example` as the shared configuration template.

## Commands

- `make install` — create `.venv` and install all dependencies
- `make dev` — start Postgres, the API, and the Vite development server
- `make test` — run client and server checks/tests
- `make seed` — apply migrations, clear demo tables, and repopulate seed data

Stop the development servers with `Ctrl+C`. Stop Postgres separately with:

```bash
docker compose down
```

## Database migrations

Create a migration after changing models:

```bash
.venv/bin/alembic -c server/alembic.ini revision --autogenerate -m "describe change"
```

Apply migrations with:

```bash
.venv/bin/alembic -c server/alembic.ini upgrade head
```

The commands use Postgres at `localhost:5433`. The service is `db`, so use
`docker compose up -d db` rather than `docker compose up -d postgres`.

## OCR dependency

Prescription extraction uses the `pytesseract` Python package and requires the
Tesseract executable on the API host:

```bash
# macOS
brew install tesseract

# Debian/Ubuntu
sudo apt-get install tesseract-ocr
```

If the executable is unavailable, the extraction endpoint returns HTTP 503.

## Backend deployment

The API ships as a container built from `server/Dockerfile` and is configured for
Railway through `server/railway.json`. Any Docker host works the same way.

### Container behaviour

`server/docker-entrypoint.sh` starts the process:

- listens on `$PORT` (default `8000`) with `$WEB_CONCURRENCY` Uvicorn workers
- runs `--proxy-headers` so client IPs and scheme survive the platform's proxy
- runs migrations first when `RUN_MIGRATIONS=1`, for hosts without a pre-deploy
  hook; Railway leaves it at `0` and uses the `preDeployCommand` instead
- runs as the unprivileged `appuser`, and the image carries a Docker
  `HEALTHCHECK` against `/api/health`

Build and run it locally:

```bash
docker build -t swaddle-api server
docker run --rm -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg://swaddle:swaddle@host.docker.internal:5433/swaddle" \
  -e CORS_ORIGINS="http://localhost:5173" \
  swaddle-api
```

### Health endpoints

- `GET /api/health` — liveness; the process is up and its configuration parsed
- `GET /api/health/ready` — readiness; also runs `SELECT 1` against the database
  and returns HTTP 503 when it is unreachable

The platform health check targets `/api/health/ready` so a deploy with a broken
`DATABASE_URL` fails fast instead of serving errors.

### Environment variables

Set these on the host; `.env.example` lists the full set with defaults.

| Variable | Required | Notes |
| --- | --- | --- |
| `DATABASE_URL` | yes | `postgres://` and `postgresql://` are rewritten to the psycopg driver |
| `OPENAI_API_KEY` | yes | symptom check and prescription extraction |
| `CORS_ORIGINS` | yes | comma-separated exact origins of the deployed client |
| `CORS_ORIGIN_REGEX` | no | pattern for generated hostnames, e.g. Netlify deploy previews |
| `DB_POOL_SIZE`, `DB_MAX_OVERFLOW` | no | per-worker pool; total connections are the pool times `WEB_CONCURRENCY` |
| `DB_POOL_RECYCLE_SECONDS` | no | recycles connections before managed Postgres drops them (default `1800`) |
| `WEB_CONCURRENCY` | no | Uvicorn worker count (default `2`) |
| `LOG_LEVEL` | no | Uvicorn log level (default `info`) |
| `RUN_MIGRATIONS` | no | `1` to migrate on container start (default `0`) |
| `CLOUDINARY_URL` | no | prescription media storage |

Keep `DB_POOL_SIZE` times `WEB_CONCURRENCY` under the connection limit of the
Postgres plan.

## How We Used Codex & GPT-5.6

This project was built using an idea-first, Codex-driven workflow: the concept,
problem framing, feature scope, and technology-stack decisions were made
independently, then the implementation was generated through Codex via
natural-language prompts and iterated with manual smoke testing and automated
checks. GPT-5.6 powers the application's structured symptom-check, prescription
extraction, and optional product re-ranking paths.

### Key decisions made independently

- **Problem and scope**: identified the fragmented baby-care experience—health
  guidance, prescriptions, products, developmental content, and pediatric access
  living in separate apps or services—and defined Swaddle as the unifying
  platform.
- **Feature scoping for safety**: deliberately constrained the AI Baby Assistant
  to never suggest specific medicines or dosages, and the Prescription Extractor
  to extract and structure text only, not confirm medical correctness. This was
  a conscious product decision intended to prevent the platform from practicing
  medicine, not a Codex suggestion.
- **Technology stack**: chose React, TypeScript, Vite, and Tailwind CSS for the
  client and FastAPI on Python 3.11 for the server, with shared type definitions
  to keep the client/server contract consistent.
- **Data model and architecture**: defined the core entities (`User`, `Baby`,
  `SymptomQuery`, `Prescription`, `Product`, `ContentItem`, and
  `ConsultationSlot`) and the overall system structure documented in
  [ARCHITECTURE.md](ARCHITECTURE.md).
- **What to leave out of this build**: explicitly descoped real pharmacy and
  clinic integrations, live 24-hour video consultations, durable production file
  storage, and payment processing as roadmap items rather than presenting them
  as working features.

### Where Codex and GPT-5.6 did the work

The implementation files—including backend models, FastAPI routes and services,
OCR integration, AI prompt and structured-response handling, React components
and pages, Alembic migrations, and Docker/Makefile tooling—were generated by
prompting Codex in natural language and iterating on its output. Prompts were
written task by task, such as “scaffold the monorepo,” “build the symptom-check
endpoint with these safety constraints,” and “build the prescription extractor
using OCR and GPT-5.6 structuring,” rather than as one large specification. This
allowed each piece to be reviewed before moving to the next.

Within the running application, GPT-5.6 is used through the OpenAI Responses API
for strict structured output. Deterministic server code remains responsible for
request validation, medical red-flag overrides, fixed disclaimers, authorization,
timeouts, persistence, and error handling.

### Verification

After each Codex-generated module, functionality was manually smoke-tested by
running the development stack, exercising endpoints and pages, and checking edge
cases such as empty states and alert-level enforcement. The repository also
contains automated pytest endpoint and validation coverage plus client linting,
formatting, type-checking, and production-build checks, all run through
`make test`.

### Why this workflow

This build intentionally explored how far an idea-and-decisions-driven,
Codex-generated implementation could go for a non-trivial, multi-service
platform. Codex served as the engineering execution layer, GPT-5.6 powers the
application's structured AI workflows, and product judgment, safety scoping, and
architecture remained in human hands.

## License

Swaddle is available under the [MIT License](LICENSE).
