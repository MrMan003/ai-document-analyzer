"""
Prometheus metrics collection.
"""
import time
from functools import wraps
from typing import Callable, Any

from prometheus_client import Counter, Histogram, Gauge

# Metrics definitions
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
)

DOCUMENT_PROCESSING_DURATION = Histogram(
    "document_processing_duration_seconds",
    "Document processing duration",
    ["status"],
    buckets=[5, 10, 30, 60, 120, 300, 600]
)

ACTIVE_DOCUMENTS = Gauge(
    "active_documents",
    "Number of documents currently being processed"
)

RISK_COUNTER = Counter(
    "risks_identified_total",
    "Total risks identified",
    ["severity", "category"]
)

TOKENS_USED = Counter(
    "llm_tokens_used_total",
    "Total LLM tokens used",
    ["model"]
)


def track_processing_time(metric_name: str):
    """Decorator to track processing time."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status = "success"
                return result
            except Exception as e:
                status = "failed"
                raise
            finally:
                duration = time.time() - start_time
                # Record in appropriate metric
                if metric_name == "document":
                    DOCUMENT_PROCESSING_DURATION.labels(status=status).observe(duration)
        return wrapper
    return decorator