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
    # Cloudflare sits in front of Render and always overwrites this header at
    # its own edge, so it's the one value here a client can't spoof. Fall
    # back to the last X-Forwarded-For hop (appended by the nearest trusted
    # proxy) rather than the first (attacker-controlled, since proxies
    # append to the end of the list, not overwrite the front).
    cf_connecting_ip = request.headers.get("cf-connecting-ip")
    if cf_connecting_ip:
        return cf_connecting_ip.strip()
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


def is_owner(request: Request) -> bool:
    owner_key = get_settings().owner_access_key
    if not owner_key:
        return False
    provided = request.headers.get(OWNER_HEADER, "")
    return secrets.compare_digest(provided, owner_key)


def require_owner(request: Request) -> None:
    if not is_owner(request):
        raise HTTPException(status_code=403, detail="Only the owner can do that.")


def enforce_rate_limit(request: Request) -> None:
    if is_owner(request):
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
