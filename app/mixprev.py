"""Preview clips for the decks and one-tap previews: the track's 30-second Deezer preview, passed through to
the browser (which finds the beats itself). Clips are held in memory for a short while only, never written to disk."""
import threading
from collections import OrderedDict

from app import sources

_clips: OrderedDict[int, bytes] = OrderedDict()
_lock = threading.Lock()
MAX_CLIPS = 24          # about 12 MB of 30-second previews


def clip(deezer_id: int) -> bytes:
    """The track's 30-second Deezer preview (MP3 bytes)."""
    with _lock:
        if deezer_id in _clips:
            _clips.move_to_end(deezer_id)
            return _clips[deezer_id]
    url = (sources.deezer_track(deezer_id) or {}).get("preview")
    if not url:
        raise LookupError("no preview")
    data = sources.fetch_preview(url)
    with _lock:
        _clips[deezer_id] = data
        while len(_clips) > MAX_CLIPS:
            _clips.popitem(last=False)
    return data
