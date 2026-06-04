from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from redis import Redis

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.core.metrics import metrics_middleware, metrics_response
from app.database.session import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis = redis
    yield
    redis.close()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Centralized cloud operations platform for infrastructure visibility and incident response.",
    lifespan=lifespan,
)

app.middleware("http")(metrics_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    db = SessionLocal()
    db_status = "ok"
    redis_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
    finally:
        db.close()

    try:
        app.state.redis.ping()
    except Exception:
        redis_status = "error"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"
    return {"status": overall, "database": db_status, "redis": redis_status}


@app.get("/metrics", tags=["system"])
def metrics():
    return metrics_response()


app.include_router(api_router, prefix=settings.api_v1_prefix)
