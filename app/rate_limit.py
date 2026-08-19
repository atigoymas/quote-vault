import time
from collections import defaultdict

from fastapi import HTTPException, Request

# Shared across every Gemini-calling route — the scarce resource being
# protected is the API quota, not any single endpoint.
WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 10

_hits: dict[str, list[float]] = defaultdict(list)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def enforce_rate_limit(request: Request) -> None:
    client_ip = _client_ip(request)
    now = time.monotonic()
    window_start = now - WINDOW_SECONDS
    hits = _hits[client_ip]
    while hits and hits[0] < window_start:
        hits.pop(0)
    if len(hits) >= MAX_REQUESTS_PER_WINDOW:
        raise HTTPException(status_code=429, detail="Too many requests — slow down a bit.")
    hits.append(now)


def reset() -> None:
    _hits.clear()
