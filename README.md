# SimilarSounds (prototype)

Paste a YouTube / SoundCloud / Beatport / Deezer link (or type `Artist - Title`) and get
house tracks that match on **sound, key (Camelot), BPM and energy**, with the newest
releases boosted to the top.

## Run it

```bash
./.tools/uv run python -m scripts.seed --per-style 100   # build / top up the catalogue (run daily)
./.tools/uv run uvicorn app.main:app --port 8000          # then open http://localhost:8000
```

## How it works

| File | What it does |
|---|---|
| `app/sources.py` | Reads pasted links (YouTube/SoundCloud oEmbed, Beatport slug, Deezer), finds the track on Deezer |
| `app/analysis.py` | From a 30s preview (in memory, never saved): Camelot key, BPM, energy features, timbre fingerprint |
| `app/catalogue.py` | SQLite storage + in-memory index; energy mapped to 1-10 against the catalogue |
| `app/ranking.py` | `score = similarity³ × key × BPM × energy × recency` (recency boost halves every 90 days) |
| `scripts/seed.py` | Pulls house tracks per sub-genre from Deezer playlists, newest years first |
| `static/index.html` | The web page |

## Stand-ins to replace later

- **Deezer** is the temporary preview + metadata source. Its API terms are **non-commercial only** -
  fine for a private prototype, not for a public / ad-supported launch.
- **Beatport partner API** should replace it: official key/BPM/genre, release dates and previews.
- **Fingerprint** is a hand-built librosa feature vector. Upgrade path: Essentia Discogs-EffNet
  embeddings (better similarity and automatic sub-genre tagging).
- **SQLite + numpy** works to ~100k tracks; move to Postgres + pgvector after that.
