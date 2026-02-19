# Job Tracker API

[![CI](https://github.com/nayfly/Job-Tracker-API/actions/workflows/ci.yml/badge.svg)](https://github.com/nayfly/Job-Tracker-API/actions)

A simple FastAPI backend used to track job applications, companies and follow-ups.
This project is designed as a technical portfolio piece with:

- authentication (register/login) using JWT
- company & application CRUD operations
- follow-up notes tied to applications
- SQLite fallback for local development and testing
- SQLAlchemy + Alembic for data models and migrations


## Architecture

```mermaid
flowchart LR
    subgraph API
        A[FastAPI app] -->|includes routers| R[Auth / Companies / Applications / Followups]
        A --> M[RequestIdMiddleware]
    end
    A --> DB[(Database)]
    style DB fill:#f9f,stroke:#333,stroke-width:2px
    note right of M
      assigns unique
      request_id to each
      incoming HTTP call
    end
```

## Technical decisions & logging

* **Argon2 for password hashing** – new passwords are hashed with Argon2 (memory-hard, GPU-resistant). bcrypt is still accepted for backward
  compatibility. The helper `needs_rehash()` can be used to transparently
  upgrade legacy hashes on successful login
* **JWT with HS256** – symmetric signing keeps the implementation
  simple; tokens contain only the user email (`sub`) and expiration.
  HS256 is widely supported and appropriate for a single‑service API.

Request logging is structured and enriched with a `request_id` from
`app/middleware/request_id.py`. Every handler can include this ID in
logs to trace individual requests across async calls.

## Example JWT payload

```json
{
  "sub": "user@example.com",
  "exp": 1740000000
}
```

(The `access_token` is a base64‑encoded header.payload.signature string.)

## Getting Started


### Python environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# or source .venv/bin/activate on macOS/Linux
pip install -e .[dev]
```

The `pyproject.toml` defines dependencies and `ruff` for linting.

### Configuration

Settings come from environment variables or a `.env` file.
The following variables are recognized (defaults shown):

| Name | Default | Description |
|------|---------|-------------|
| `ENV` | `local` | application environment (`test` triggers in-memory SQLite) |
| `SECRET_KEY` | `change-me` | JWT signing key |
| `DATABASE_URL` | computed | full SQLAlchemy URL, fallback to SQLite if not set |

For a simple local run you can leave `DATABASE_URL` unset and a file
`./db.sqlite3` will be used automatically. Tests set `ENV=test` and
use an in-memory database.

### Running the server

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

### Running tests

```bash
pip install -e .[dev]
pytest -q
```

The test suite includes both unit and integration tests. A shared
`tests/conftest.py` sets up a temporary SQLite database and adjusts
FastAPI dependencies so the code under test uses the right engine.

### Linting

```bash
ruff check --fix .
```

## Database migrations

Alembic is configured in `alembic/`. To create a migration:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## API Overview

- `POST /auth/register` – create new user
- `POST /auth/login` – obtain bearer token
- `GET /health` – healthcheck
- `GET/POST/DELETE /companies` – manage companies (deletion is supported)
- `GET/POST/DELETE /applications` – manage applications
- `GET/POST/DELETE /followups` – manage follow-up notes

Authentication is required for most endpoints. Use the returned JWT in
`Authorization: Bearer <token>` header.

## Notes

Designed for portfolio/demo use: defaults favor fast local execution 
(SQLite) and deterministic tests. For production: configure Postgres, rotate
secrets, enforce HTTPS, and consider asymmetric JWT signing.
