import time
from typing import Callable

from fastapi import Request
from prometheus_client import Counter, Histogram

"""Prometheus metrics instrumentation and middleware for the FastAPI app."""

REQUEST_COUNT = Counter(
    "request_count",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY_SECOND = Histogram(
    "request_latency_second",
    "Request latency in seconds",
    ["method", "endpoint"],
)
ERROR_COUNT = Counter(
    "error_count",
    "Total HTTP error responses",
    ["method", "endpoint", "status"],
)

async def metrics_middleware(request: Request, call_next):
        method = request.method
        endpoint = request.url.path

        start_time = time.time()
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            ERROR_COUNT.labels(
                method=method, 
                endpoint=endpoint, 
                status=str(status_code)).inc()
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint, 
                status=str(status_code)).inc()
            REQUEST_LATENCY_SECOND.labels(
                method=method, 
                endpoint=endpoint).observe(time.time()-start_time)
            raise
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method = method,
            endpoint = endpoint,
            status = str(status_code),
        ).inc()
        REQUEST_LATENCY_SECOND.labels(
            method = method,
            endpoint = endpoint,
        ).observe(duration)
        if status_code >= 400:
            ERROR_COUNT.labels(
                method = method,
                endpoint = endpoint,
                status=str(status_code),
            ).inc()
        return response
    