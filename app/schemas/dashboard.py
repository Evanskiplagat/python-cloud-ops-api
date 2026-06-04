from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_servers: int
    active_deployments: int
    open_incidents: int
    uptime_percentage: float
    environment_overview: dict[str, int]
