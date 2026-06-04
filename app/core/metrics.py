from time import perf_counter

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "cloudops_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "cloudops_http_request_latency_seconds",
    "HTTP request latency",
    ["method", "path"],
)


async def metrics_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    start = perf_counter()
    response = await call_next(request)
    duration = perf_counter() - start
    REQUEST_COUNT.labels(method=method, path=path, status_code=response.status_code).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
    return response


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
