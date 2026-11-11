"""Visitor star reviews.

Each review is saved in Supabase (table site_reviews), where the private stats page (/stats) shows them.
Nothing personal is stored: just the time, the stars, the site language, the play count and any
comment typed into the "How can we improve?" box at the bottom of the page.
"""

import httpx


def save(stars: int, lang: str, plays: int, comment: str = "", source: str = "popup") -> None:
    from app import tokens
    if not tokens.ENABLED:
        return
    try:
        r = tokens._client.post(f"{tokens.URL}/rest/v1/rpc/add_review",
                                headers={"apikey": tokens.KEY, "Content-Type": "application/json"},
                                json={"p_stars": stars, "p_lang": lang, "p_plays": plays,
                                      "p_comment": comment or None, "p_source": source})
        if r.status_code >= 300:
            print(f"reviews: Supabase didn't save a review ({r.status_code} {r.text[:120]})", flush=True)
    except httpx.HTTPError as e:
        print(f"reviews: couldn't reach Supabase ({e})", flush=True)
