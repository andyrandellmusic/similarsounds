"""Search tokens: 3 free searches per device, 2 more with a free account, unlimited with a
subscription. Counting happens in Supabase (search_tokens function, docs/supabase/02_search_tokens.sql)
so it survives restarts. If Supabase can't be reached, searches are allowed rather than blocked."""

import hashlib
import os
import uuid

import httpx

URL = os.environ.get("SUPABASE_URL", "https://ggcohybfbbspoeccdkud.supabase.co").strip()
KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()
SALT = os.environ.get("TOKEN_SALT", "similarsounds-free-searches")
ENABLED = bool(KEY)

_client = httpx.Client(timeout=4)


def device_id(raw: str | None) -> str:
    try:
        return str(uuid.UUID(raw or ""))
    except ValueError:
        return str(uuid.uuid4())   # no or bad id: counts against the network's daily free limit


def client_ip(request) -> str:
    """The visitor's real address. Render sits behind Cloudflare, which sets CF-Connecting-IP itself and
    refuses requests that try to fake it; X-Forwarded-For can be made up by anyone, so it isn't trusted."""
    return (request.headers.get("cf-connecting-ip") or request.headers.get("true-client-ip")
            or (request.client.host if request.client else "")).strip()


def ip_hash(request) -> str:
    return hashlib.sha256(f"{SALT}:{client_ip(request)}".encode()).hexdigest()[:32]


def check(request, seed: int | None, consume: bool) -> dict | None:
    """Ask Supabase whether this search is allowed (and use a token if consume). None = not metered."""
    if not ENABLED:
        return None
    headers = {"apikey": KEY, "Content-Type": "application/json"}
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer ") and auth.count(".") == 2:   # a signed-in visitor's session
        headers["Authorization"] = auth
    body = {"p_device": device_id(request.headers.get("x-device-id")), "p_ip": ip_hash(request),
            "p_seed": seed, "p_consume": consume}
    try:
        r = _client.post(f"{URL}/rest/v1/rpc/search_tokens", headers=headers, json=body)
        if r.status_code == 401 and "Authorization" in headers:     # expired session: count as signed out
            print(f"tokens: login not accepted ({r.text[:120]}), counting as signed out", flush=True)
            headers.pop("Authorization")
            r = _client.post(f"{URL}/rest/v1/rpc/search_tokens", headers=headers, json=body)
        r.raise_for_status()
        return r.json()
    except (httpx.HTTPError, ValueError):
        return None


def vote(request, seed: int, match: int, value: int, rank=None, similarity=None, mix=None) -> bool:
    """Save a thumbs up (1) / down (-1) / undo (0) on one match. Never blocks the page."""
    if not ENABLED:
        return False
    headers = {"apikey": KEY, "Content-Type": "application/json"}
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer ") and auth.count(".") == 2:
        headers["Authorization"] = auth
    body = {"p_device": device_id(request.headers.get("x-device-id")), "p_seed": seed, "p_match": match,
            "p_vote": value, "p_rank": rank, "p_similarity": similarity, "p_mix": mix}
    try:
        r = _client.post(f"{URL}/rest/v1/rpc/record_vote", headers=headers, json=body)
        if r.status_code == 401 and "Authorization" in headers:
            headers.pop("Authorization")
            r = _client.post(f"{URL}/rest/v1/rpc/record_vote", headers=headers, json=body)
        return r.status_code < 300
    except httpx.HTTPError:
        return False


def count_play(deezer_id: int) -> bool:
    """One play of a track's preview, for the "Most played" list. Never blocks the page."""
    if not ENABLED:
        return False
    try:
        r = _client.post(f"{URL}/rest/v1/rpc/count_play", headers={"apikey": KEY, "Content-Type": "application/json"},
                         json={"p_id": deezer_id})
        return r.status_code < 300
    except httpx.HTTPError:
        return False


def top_played(days: int = 7, limit: int = 30) -> list[tuple[int, int]]:
    """[(deezer_id, plays)] most played first, over the last `days` days. Empty if Supabase can't be reached."""
    if not ENABLED:
        return []
    try:
        r = _client.post(f"{URL}/rest/v1/rpc/top_played", headers={"apikey": KEY, "Content-Type": "application/json"},
                         json={"p_days": days, "p_limit": limit})
        r.raise_for_status()
        return [(int(x["deezer_id"]), int(x["plays"])) for x in r.json()]
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return []
