from fastapi import APIRouter

from app.api.routes import auth, dashboard, deployments, incidents, servers, uptime

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(servers.router, prefix="/servers", tags=["servers"])
api_router.include_router(deployments.router, prefix="/deployments", tags=["deployments"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(uptime.router, prefix="/uptime", tags=["uptime"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
