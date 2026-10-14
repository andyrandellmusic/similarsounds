"""Automatic genre clean-up for the whole catalogue, from:
  - Boss's listening test (eval/results/genre_labels.json)        strongest
  - Beatport's genres for 629 chart tracks (eval/results/bp_all.jsonl)
  - Discogs styles (eval/results/discogs_genres.jsonl)
  - each track's sound (CLAP fingerprint) and its record label
Writes eval/results/auto_genres.json (a plan: nothing in the catalogue changes) and prints honest
accuracy checks against Boss's answers, leaving each track's own answer out of its prediction."""
import collections, json, sqlite3, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eval.genre_model import fit, prob, FIVE

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "eval" / "results"

# Discogs styles -> our five, another house style (set aside, maybe added later) or not house at all
OURS = {"House": "House", "Acid House": "House", "Garage House": "House", "Italo House": "House", "Chicago House": "House",
        "Deep House": "Deep House", "Tech House": "Tech House", "Minimal": "Minimal / Deep Tech", "Minimal Techno": "Minimal / Deep Tech",
        "Nu-Disco": "Funky / Disco House", "Disco": "Funky / Disco House", "Boogie": "Funky / Disco House",
        "French House": "Funky / Disco House", "Funk": "Funky / Disco House"}
OTHER_HOUSE = {"Progressive House", "Tribal House", "Afrobeat", "Afro House", "Ambient House", "Speed Garage", "Latin",
               "UK Garage", "Hard House", "Deep Techno", "Leftfield"}
NOT_HOUSE = {"Techno", "Trance", "Progressive Trance", "Hard Trance", "Hard Techno", "Tech Trance", "Psy-Trance", "Neo Trance",
             "Goa Trance", "Hardcore", "Hardstyle", "Happy Hardcore", "Gabber", "Drum n Bass", "Jungle", "Dubstep", "Bass Music",
             "Dance-pop", "Synth-pop", "Europop", "Contemporary R&B", "Rhythm & Blues", "Soft Rock", "Synthwave", "Darkwave",
             "Electro House", "Future House", "Euro House", "Big Room", "Breaks", "Progressive Breaks", "Breakbeat", "IDM",
             "Experimental", "Ambient", "Downtempo", "Pop Rap", "Trap", "Electro", "Moombahton", "Eurodance", "Hip Hop"}
NON_ELECTRONIC = {"Pop", "Hip Hop", "Rock", "Folk, World, & Country", "Classical", "Reggae", "Children's", "Stage & Screen"}


def discogs_verdict(d):
    """('ours', style) / ('other', None) / ('not', None) / (None, None) when Discogs has nothing clear."""
    if not d or not d.get("match"):
        return None, None
    st, ge = d.get("styles") or [], set(d.get("genres") or [])
    ours = [OURS[s] for s in st if s in OURS]
    nots = [s for s in st if s in NOT_HOUSE]
    other = [s for s in st if s in OTHER_HOUSE]
    if "Electronic" not in ge and ge & NON_ELECTRONIC:
        return "not", None
    if nots and len(nots) >= len(ours):
        return "not", None
    if ours:          # any of our styles listed (e.g. Tech House next to Minimal Techno): it's ours
        specific = [s for s in ours if s != "House"]
        return "ours", (specific[0] if specific else "House")
    if other:
        return "other", None
    return None, None


def main():
    con = sqlite3.connect(ROOT / "data" / "catalogue.db")
    rows = {r[0]: r for r in con.execute("SELECT deezer_id, artist, title, label, style FROM tracks")}
    z = np.load(ROOT / "data" / "clap.npz"); emb = dict(zip(z["ids"].tolist(), z["emb"]))
    ids = [i for i in rows if i in emb]
    boss = {int(k): v["genre"] for k, v in json.load(open(R / "genre_labels.json")).items()}
    disc = {}
    if (R / "discogs_genres.jsonl").exists():
        for l in open(R / "discogs_genres.jsonl"):
            d = json.loads(l); disc[d["id"]] = d
    bp = [json.loads(l) for l in open(R / "bp_all.jsonl")]
    bp = [r for r in bp if r.get("clap") and r["genre"] in FIVE]
    dv = {i: discogs_verdict(disc.get(i)) for i in ids}
    # how much each track sounds like house versus trance / EDM / techno / pop (genre descriptions, CLAP)
    gt = np.load(ROOT / "data" / "clap_genre_text.npz"); gnames = list(gt["names"])
    hk = [k for k, n in enumerate(gnames) if n in set(gt["house"])]
    En = np.array([emb[i] for i in ids], "float32"); En /= np.linalg.norm(En, axis=1, keepdims=True)
    S = En @ gt["emb"].T * 100; Pt = np.exp(S - S.max(1, keepdims=True)); Pt /= Pt.sum(1, keepdims=True)
    house_text = dict(zip(ids, Pt[:, hk].sum(1)))
    label_of = {i: (rows[i][3] or "").strip() for i in ids}

    # ---------- 1. "ours" vs "not ours" by sound, trained on everything that has an answer ----------
    def ours_training(exclude=frozenset()):
        X, y = [], []
        for r in bp:
            X.append(r["clap"]); y.append(0)
        for i, g in boss.items():
            if i in emb and i not in exclude:
                X.append(emb[i]); y.append(1 if g == "Not our genres" else 0)
        for i, (v, _) in dv.items():
            if v and i not in boss and i not in exclude:
                X.append(emb[i]); y.append(0 if v == "ours" else 1)
        return np.array(X, "float32"), np.array(y)

    # honest check: sound model trained without Boss's answers, scored on Boss's 100
    X, y = ours_training(exclude=frozenset(boss))
    m_ours = fit(X, y, 2)
    bi = [i for i in boss if i in emb and i in dv]          # tracks still on the site
    p_b = prob(m_ours, np.array([emb[i] for i in bi]))[:, 1]

    # ---------- 2. record labels: what do the answered tracks on each label say? ----------
    def label_votes(skip=None):
        v = collections.defaultdict(lambda: [0.0, 0.0])          # [ours, not]
        for i in ids:
            if i == skip or not label_of[i]:
                continue
            if i in boss:
                v[label_of[i]][1 if boss[i] == "Not our genres" else 0] += 2
            elif dv[i][0]:
                v[label_of[i]][0 if dv[i][0] == "ours" else 1] += 1
        return v

    def label_verdict(lv, lab):
        o, n = lv.get(lab, (0, 0))
        if o + n >= 3 and n / (o + n) >= 0.7:
            return "not"
        if o + n >= 3 and o / (o + n) >= 0.7:
            return "ours"
        return None

    def decide(i, p_not, lv, use_boss=True, use_discogs=True):
        # order of trust: Discogs, then Boss's listening test, then sound + record label
        d = dv[i][0] if use_discogs else None
        if d in ("not", "other"):
            return "not"
        if d == "ours":
            return "ours"
        if use_boss and i in boss:
            return "not" if boss[i] == "Not our genres" else "ours"
        lab = label_verdict(lv, label_of[i])
        if d in ("not", "other") and lab != "ours" and p_not >= 0.4:
            return "not"
        if lab == "not" and d != "ours" and p_not >= 0.4:
            return "not"
        if p_not >= 0.85 and lab != "ours" and d != "ours":
            return "not"
        if p_not >= 0.6 and house_text[i] < 0.35 and lab != "ours" and d != "ours":
            return "not"
        return "ours"

    # honest check against Boss's 100: his own answer, label vote and the sound model all leave the track out
    agree = tp = fn = fp = 0
    for i, p in zip(bi, p_b):
        pred = decide(i, p, label_votes(skip=i), use_boss=False)
        truth = "not" if boss[i] == "Not our genres" else "ours"
        agree += pred == truth; tp += pred == truth == "not"; fn += truth == "not" and pred == "ours"; fp += truth == "ours" and pred == "not"
    n_not = sum(1 for i in bi if boss[i] == "Not our genres")
    print(f"ours-vs-not, checked against your 100 (your answers hidden): {agree}/{len(bi)} agree; "
          f"caught {tp}/{n_not} of your 'not ours'; wrongly set aside {fp}/{len(bi) - n_not} keepers", flush=True)

    # ---------- 3. sub-genres: sound + label tendency, trained on Beatport + Boss + specific Discogs styles ----------
    def five_training(exclude=frozenset()):
        X, y = [], []
        for r in bp:
            X.append(r["clap"]); y.append(FIVE.index(r["genre"]))
        for i, g in boss.items():
            if g in FIVE and i in emb and i not in exclude:
                X.append(emb[i]); y.append(FIVE.index(g))
        for i, (v, s) in dv.items():
            if v == "ours" and s and s != "House" and i not in boss and i not in exclude:
                X.append(emb[i]); y.append(FIVE.index(s))
        return np.array(X, "float32"), np.array(y)

    def label_style_prior(skip=None):
        c = collections.defaultdict(lambda: np.ones(5))           # +1 smoothing
        for i in ids:
            if i == skip or not label_of[i]:
                continue
            g = boss.get(i) if boss.get(i) in FIVE else (dv[i][1] if dv[i][0] == "ours" else None)
            if g:
                c[label_of[i]][FIVE.index(g)] += 2 if i in boss else 1
        return c

    X5, y5 = five_training(exclude=frozenset(boss))
    m5 = fit(X5, y5, 5)
    kept = [i for i in bi if boss[i] in FIVE]
    P = prob(m5, np.array([emb[i] for i in kept]))
    for w in (0.0, 0.5, 1.0, 2.0):
        hit = 0
        for k, i in enumerate(kept):
            pr = label_style_prior(skip=i)[label_of[i]] if label_of[i] else np.ones(5)
            score = np.log(P[k] + 1e-9) + w * np.log(pr / pr.sum())
            hit += FIVE[int(score.argmax())] == boss[i]
        site = sum(rows[i][4] == boss[i] for i in kept)
        print(f"sub-genre vs your answers (label weight {w}): {hit}/{len(kept)}   (site now {site}/{len(kept)})", flush=True)

    if "--plan" not in sys.argv:
        return
    W = float(sys.argv[sys.argv.index("--w") + 1]) if "--w" in sys.argv else 1.0
    # Boss's rekordbox USB genre tags count as his answers too (only for the plan, not the checks above)
    if (R / "usb_refs.jsonl").exists():
        for l in open(R / "usb_refs.jsonl"):
            u = json.loads(l)
            if u.get("deezer_id") in rows and u["genre"] in FIVE:
                boss.setdefault(u["deezer_id"], u["genre"])
    # ---------- 4. the plan for every track, with all evidence (Boss's answers included) ----------
    Xo, yo = ours_training(); m_ours = fit(Xo, yo, 2)
    X5, y5 = five_training(); m5 = fit(X5, y5, 5)
    E = np.array([emb[i] for i in ids], "float32")
    p_not = prob(m_ours, E)[:, 1]; P5 = prob(m5, E)
    lv = label_votes(); lp = label_style_prior()
    gt = np.load(ROOT / "data" / "clap_genre_text.npz"); tnames = list(gt["names"])
    T = (E / np.linalg.norm(E, axis=1, keepdims=True)) @ gt["emb"].T
    plan = []
    for k, i in enumerate(ids):
        verdict = decide(i, float(p_not[k]), lv)
        if verdict == "not":
            kind = "other house style" if (dv[i][0] == "other" or tnames[int(T[k].argmax())] in ("melodic house", "afro house")) else "not house"
            why = "Discogs" if dv[i][0] in ("not", "other") else "your test" if i in boss else "sound and label"
            plan.append({"id": i, "action": "set aside", "kind": kind, "why": why, "site_style": rows[i][4]})
            continue
        if dv[i][0] == "ours" and dv[i][1] != "House":
            style = dv[i][1]
        elif i in boss and boss[i] in FIVE:
            style = boss[i]
        elif dv[i][0] == "ours" and dv[i][1] == "House" and rows[i][4] not in FIVE:
            style = "House"
        else:
            style = rows[i][4]                    # no direct evidence: keep the current sub-genre
        plan.append({"id": i, "action": "keep", "style": style, "site_style": rows[i][4]})
    json.dump(plan, open(R / "auto_genres.json", "w"))
    # what the daily update needs to check new tracks the same way (sound model + labels that aren't ours)
    not_labels = sorted(l for l in lv if l and label_verdict(lv, l) == "not")
    np.savez(ROOT / "data" / "genre_check.npz", mu=m_ours["mu"], sd=m_ours["sd"], W=m_ours["W"], b=m_ours["b"],
             text_emb=gt["emb"], text_names=gt["names"], house=gt["house"], not_labels=np.array(not_labels))
    print("saved data/genre_check.npz with", len(not_labels), "labels that aren't ours")
    c = collections.Counter(p["action"] for p in plan)
    ka = collections.Counter(p["kind"] for p in plan if p["action"] == "set aside")
    ch = sum(1 for p in plan if p["action"] == "keep" and p["style"] != p["site_style"])
    print(f"plan: keep {c['keep']}, set aside {c['set aside']} ({dict(ka)}); sub-genre changes on kept tracks: {ch}")
    print("set aside because of:", dict(collections.Counter(p["why"] for p in plan if p["action"] == "set aside")))
    print("kept styles:", collections.Counter(p["style"] for p in plan if p["action"] == "keep"))


if __name__ == "__main__":
    main()
