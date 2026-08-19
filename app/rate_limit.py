import secrets
import time
from collections import defaultdict

from fastapi import HTTPException, Request

from app.config import get_settings

# Shared across every Gemini-calling route — the scarce resource being
# protected is the API quota, not any single endpoint.
#
# The owner's browser sends OWNER_HEADER (set once via a private link, never
# baked into the public build) and bypasses this entirely. Everyone else —
# including anyone who finds this deployment's public source or URL — gets
# a small daily allowance, enough to see the app work once, not enough to
# matter against a tiny Gemini quota.
OWNER_HEADER = "x-owner-key"
PUBLIC_WINDOW_SECONDS = 60 * 60 * 24
PUBLIC_MAX_REQUESTS_PER_WINDOW = 3

_hits: dict[str, list[float]] = defaultdict(list)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _is_owner(request: Request) -> bool:
    owner_key = get_settings().owner_access_key
    if not owner_key:
        return False
    provided = request.headers.get(OWNER_HEADER, "")
    return secrets.compare_digest(provided, owner_key)


def enforce_rate_limit(request: Request) -> None:
    if _is_owner(request):
        return

    client_ip = _client_ip(request)
    now = time.monotonic()
    window_start = now - PUBLIC_WINDOW_SECONDS
    hits = _hits[client_ip]
    while hits and hits[0] < window_start:
        hits.pop(0)
    if len(hits) >= PUBLIC_MAX_REQUESTS_PER_WINDOW:
        raise HTTPException(status_code=429, detail="Too many requests — slow down a bit.")
    hits.append(now)


def reset() -> None:
    _hits.clear()
