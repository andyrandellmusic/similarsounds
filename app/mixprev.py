"""'Hear the mix': hands the browser two preview clips and where their beats fall, so it can beatmatch
and crossfade them like a DJ. Clips are held in memory for a short while only, never written to disk."""
import threading
from collections import OrderedDict

import librosa
import numpy as np

from app import sources
from app.analysis import SR, load_audio

_clips: OrderedDict[int, bytes] = OrderedDict()
_grids: dict[tuple[int, float], dict] = {}
_lock = threading.Lock()
MAX_CLIPS = 40          # about 20MB of 30-second previews


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


def beat_grid(deezer_id: int, bpm: float) -> dict:
    """Fine-tune the BPM and find where the beats land in the preview: try tempos close to the known BPM
    and every phase, keep the grid that sits on the strongest hits (the kick drum in house, listened to on its own so the off-beat hi-hats can't pull the grid half a beat out)."""
    key = (deezer_id, round(bpm, 1))
    if key in _grids:
        return _grids[key]
    y = load_audio(clip(deezer_id))
    hop = 256
    env = librosa.onset.onset_strength(y=y, sr=SR, hop_length=hop, fmax=160, n_mels=24)   # the kick drum only, not off-beat hats
    env = env / (env.max() + 1e-9)
    fps, n = SR / hop, len(env)
    best = (-1.0, bpm, 0.0)
    for b in np.arange(bpm - 0.6, bpm + 0.61, 0.05):
        period = 60.0 / b
        for phase in np.arange(0, period, 0.004):
            frames = np.round((phase + period * np.arange(int((n / fps - phase) / period))) * fps).astype(int)
            frames = frames[frames < n]
            score = env[frames].mean() if len(frames) else 0
            if score > best[0]:
                best = (score, b, phase)
    out = {"bpm": round(float(best[1]), 3), "phase": round(float(best[2]), 4), "dur": round(len(y) / SR, 2)}
    _grids[key] = out
    return out
