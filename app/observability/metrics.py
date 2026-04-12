from __future__ import annotations

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNT = Counter("request_count", "Number of incoming requests")
SUCCESS_COUNT = Counter("success_count", "Number of successful requests")
ERROR_COUNT = Counter("error_count", "Number of failed requests")
FALLBACK_COUNT = Counter("fallback_count", "Number of fallback activations", ["step"])
LATENCY_TOTAL = Histogram("latency_total_seconds", "Total request latency")
STEP_LATENCY = Histogram("step_latency_seconds", "Latency per pipeline step", ["step"])
EMPTY_RESULTS_COUNT = Counter("empty_results_count", "Number of requests with empty results")

metrics_router = APIRouter()


@metrics_router.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
