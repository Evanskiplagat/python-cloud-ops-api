# CloudOps Center Architecture

CloudOps Center is a FastAPI-based internal platform for infrastructure visibility, deployment tracking, incident coordination, and uptime reporting.

## Layers

- `app/api`: HTTP routes and dependency wiring.
- `app/services`: Business use cases and transaction boundaries.
- `app/repositories`: Query and persistence helpers.
- `app/models`: SQLAlchemy ORM entities.
- `app/schemas`: Pydantic request and response models.
- `app/core`: Configuration, security, pagination, logging, metrics, and error handling.

## Operational Concerns

- PostgreSQL is the system of record.
- Redis is attached for operational integrations and readiness expansion.
- Prometheus scrapes `/metrics`.
- Alembic manages schema evolution.
- GitHub Actions runs linting, security checks, tests, and Docker build validation.
