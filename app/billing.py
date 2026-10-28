"""SimilarSounds Unlimited: unlimited searches for £4.99 a month, paid through Stripe Checkout.

Switched OFF until SUBSCRIPTIONS_ON=1 is set on Render. Deezer's API terms are non-commercial, so it stays off
until Deezer (or Beatport, or another licensed source) agrees to paid use. Everything else is ready:
    STRIPE_SECRET_KEY      Stripe secret key (sk_live_... or sk_test_...)
    STRIPE_PRICE_ID        the £4.99 / month price (price_...)
    STRIPE_WEBHOOK_SECRET  signing secret of the webhook pointing at /api/stripe/webhook (whsec_...)
    SUPABASE_SERVICE_KEY   Supabase service-role key, so a payment can mark the account as subscribed
A subscriber is a row in public.subscriptions with status active / trialing (the search_tokens function already
gives those accounts unlimited searches). Rows whose customer_ref starts with "owner" are never touched.
"""
import hashlib
import hmac
import os
import time

import httpx

from app import tokens

ON = os.environ.get("SUBSCRIPTIONS_ON", "").strip() == "1"
STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "").strip()
PRICE = os.environ.get("STRIPE_PRICE_ID", "").strip()
HOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
SITE = "https://" + (os.environ.get("CANONICAL_HOST", "").strip() or "www.similarsounds.com")

_client = httpx.Client(timeout=20)


def enabled() -> bool:
    """Can people subscribe right now? Needs the switch on and every key in place."""
    return ON and bool(STRIPE_KEY and PRICE and HOOK_SECRET and SERVICE_KEY and tokens.KEY)


def _stripe(method: str, path: str, data: dict | None = None) -> dict:
    r = _client.request(method, f"https://api.stripe.com/v1{path}", data=data, auth=(STRIPE_KEY, ""))
    r.raise_for_status()
    return r.json()


def _db_headers() -> dict:
    return {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}", "Content-Type": "application/json"}


def signed_in_user(request) -> dict | None:
    """The logged-in visitor (id, email) from their Supabase session, or None."""
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer ") or not tokens.KEY:
        return None
    try:
        r = _client.get(f"{tokens.URL}/auth/v1/user", headers={"apikey": tokens.KEY, "Authorization": auth})
        if r.status_code != 200:
            return None
        u = r.json()
        return {"id": u["id"], "email": u.get("email") or ""} if u.get("id") else None
    except (httpx.HTTPError, ValueError, KeyError):
        return None


def _row(user_id: str) -> dict | None:
    r = _client.get(f"{tokens.URL}/rest/v1/subscriptions", headers=_db_headers(),
                    params={"user_id": f"eq.{user_id}", "select": "status,customer_ref,current_period_end"})
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def checkout_url(user: dict) -> str:
    """A Stripe Checkout page for £4.99 a month; back to the site afterwards."""
    data = {"mode": "subscription", "line_items[0][price]": PRICE, "line_items[0][quantity]": "1",
            "client_reference_id": user["id"], "subscription_data[metadata][user_id]": user["id"],
            "allow_promotion_codes": "true",
            "success_url": f"{SITE}/?unlimited=1", "cancel_url": f"{SITE}/?unlimited=0"}
    row = _row(user["id"])
    if row and str(row.get("customer_ref") or "").startswith("cus_"):
        data["customer"] = row["customer_ref"]              # subscribed before: same Stripe customer
    elif user["email"]:
        data["customer_email"] = user["email"]
    return _stripe("POST", "/checkout/sessions", data)["url"]


def portal_url(user: dict) -> str | None:
    """Stripe's page where a subscriber can cancel, or change their card; None if they've never paid."""
    row = _row(user["id"])
    customer = str((row or {}).get("customer_ref") or "")
    if not customer.startswith("cus_"):
        return None
    return _stripe("POST", "/billing_portal/sessions", {"customer": customer, "return_url": SITE})["url"]


def verify(payload: bytes, header: str, tolerance: int = 300) -> bool:
    """Is this webhook really from Stripe? (its Stripe-Signature header, checked with our signing secret)"""
    if not HOOK_SECRET:
        return False
    parts = [p.split("=", 1) for p in header.split(",") if "=" in p]
    ts = next((v for k, v in parts if k == "t"), "")
    sigs = [v for k, v in parts if k == "v1"]
    if not ts.isdigit() or not sigs or abs(time.time() - int(ts)) > tolerance:
        return False
    want = hmac.new(HOOK_SECRET.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(want, s) for s in sigs)


def _period_end(sub: dict) -> int | None:
    # older Stripe API versions put it on the subscription, newer ones on each item
    return sub.get("current_period_end") or next(
        (i.get("current_period_end") for i in (sub.get("items") or {}).get("data", []) if i.get("current_period_end")), None)


def _save(user_id: str, sub: dict) -> None:
    row = _row(user_id)
    if row and str(row.get("customer_ref") or "").startswith("owner"):
        return                                              # the owner's own unlimited account: leave it alone
    end = _period_end(sub)
    body = {"user_id": user_id, "status": sub.get("status") or "incomplete", "customer_ref": sub.get("customer"),
            "current_period_end": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(end)) if end else None,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    r = _client.post(f"{tokens.URL}/rest/v1/subscriptions", params={"on_conflict": "user_id"}, json=body,
                     headers={**_db_headers(), "Prefer": "resolution=merge-duplicates,return=minimal"})
    r.raise_for_status()


def handle(event: dict) -> None:
    """Keep public.subscriptions in step with Stripe: paid, renewed, payment failed, cancelled."""
    kind, obj = event.get("type", ""), (event.get("data") or {}).get("object") or {}
    if kind == "checkout.session.completed" and obj.get("mode") == "subscription":
        uid, sub_id = obj.get("client_reference_id"), obj.get("subscription")
        if uid and sub_id:
            _save(uid, _stripe("GET", f"/subscriptions/{sub_id}"))
    elif kind.startswith("customer.subscription."):
        uid = (obj.get("metadata") or {}).get("user_id")
        if uid:
            _save(uid, obj)
