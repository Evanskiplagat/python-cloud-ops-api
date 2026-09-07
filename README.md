# CloudOps Center

CloudOps Center is a backend service for recording server inventory, deployment history, incidents, and uptime checks. It is built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, Redis, Prometheus, Docker, and GitHub Actions.

## Features

- JWT authentication with RBAC for Admin, DevOps Engineer, Developer, and Viewer roles
- Server management with environment and health resource tracking
- Deployment tracking with history and status filtering
- Incident management with severity, status, resolution state, and timeline events
- Uptime target registration with checks and downtime event history
- Dashboard summary for servers, deployments, incidents, uptime, and environments
- Prometheus metrics and health endpoints
- Pagination, filtering, structured logging, and centralized exception handling

## Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- Docker and Docker Compose
- Prometheus
- Pytest
- GitHub Actions

## Project Structure

```text
cloudops-center/
|-- alembic/
|-- app/
|-- docs/
|-- monitoring/
|-- tests/
|-- .github/workflows/
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
`-- .env.example
```

## Local Setup

1. Copy `.env.example` to `.env`.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
alembic upgrade head
```

4. Start the API:

```bash
uvicorn app.main:app --reload
```

## Docker

```bash
docker-compose up --build
```

Services:

- API: `http://localhost:8000`
- OpenAPI Docs: `http://localhost:8000/docs`
- Prometheus: `http://localhost:9090`

## Example Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/dashboard/summary`
- `GET /health`
- `GET /metrics`

## Testing

```bash
python -m pytest -q
```
