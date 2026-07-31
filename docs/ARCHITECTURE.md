# Architecture Overview

## System Design

LOREWEAVE is structured as a decoupled frontend/backend monorepo.

```
Browser
  └── Next.js 15 (App Router, RSC)
        └── FastAPI (REST API)
              └── SQLAlchemy 2 (Async ORM)
                    └── SQLite (dev) / PostgreSQL (prod)
```

## API Design Principles

- Versioned under `/api/v1/`
- JSON request/response bodies validated with Pydantic v2
- Async I/O throughout (asyncpg / aiosqlite)
- Repository pattern: routers → services → repositories → ORM models

## Frontend Architecture

- App Router with React Server Components where possible
- Client components isolated to interactive islands
- Zustand for global UI state only (no server data in Zustand)
- TanStack Query owns all server state (caching, refetching, mutations)
- Feature-folder structure: each feature is self-contained

## Database

- SQLAlchemy 2 `DeclarativeBase` in `app/database/base.py`
- All models import `Base` from that module
- Alembic reads `Base.metadata` for auto-generation
- `render_as_batch=True` enables SQLite migrations

## Security Notes (implement before production)

- Rotate `SECRET_KEY` in production
- Enable HTTPS / TLS termination at the reverse proxy
- Configure `ALLOWED_ORIGINS` to the real frontend domain
- Add rate limiting (e.g., `slowapi`)
- Add authentication (e.g., OAuth2 + JWT)
