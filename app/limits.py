"""Small in-memory limits for the endpoints that cost something but don't use a search credit
(track analysis for shared sets / gap fixes, reviews, play counts). One server process, so a dict is enough;
a restart simply starts everyone afresh."""
import threading
import time
from collections import OrderedDict, deque


class RateLimit:
    """At most `limit` events per key in any `window` seconds."""

    def __init__(self, limit: int, window: float, max_keys: int = 5000):
        self.limit, self.window, self.max_keys = limit, window, max_keys
        self._hits: OrderedDict[str, deque] = OrderedDict()
        self._lock = threading.Lock()

    def allow(self, key: str, cost: int = 1) -> bool:
        now = time.monotonic()
        with self._lock:
            q = self._hits.pop(key, None) or deque()
            while q and now - q[0] > self.window:
                q.popleft()
            ok = len(q) + cost <= self.limit
            if ok:
                q.extend([now] * cost)
            self._hits[key] = q                      # most recent last; forget the oldest visitors
            while len(self._hits) > self.max_keys:
                self._hits.popitem(last=False)
            return ok


# brand-new tracks analysed without a search credit (opening a shared set, "fix this gap"): plenty for real use
free_analysis = RateLimit(limit=15, window=3600)
reviews_per_visitor = RateLimit(limit=5, window=3600)
reviews_total = RateLimit(limit=60, window=3600)
# "Most played": one play per visitor per track every 30 minutes, and no more than 200 plays an hour each
play_repeat = RateLimit(limit=1, window=1800, max_keys=20000)
plays_per_visitor = RateLimit(limit=200, window=3600)
