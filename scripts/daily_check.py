"""SimilarSounds daily check in one go: is the site up and on the latest version, did the 6am track pull run,
and what did it pull in. Prints a short plain report.

Usage: python3 scripts/daily_check.py [DAYS]      (default 3; does a `git pull` first)
"""
from pathlib import Path
import hashlib, json, os, subprocess, sys, time, urllib.request

DAYS = sys.argv[1] if len(sys.argv) > 1 else "3"
ROOT = os.path.join(os.path.dirname(__file__), "..")
SITE = "https://www.similarsounds.com"
REPO = "andyrandellmusic/similarsounds"
run = lambda *a: subprocess.run(a, cwd=ROOT, capture_output=True, text=True).stdout.strip()


def get(url, timeout=60):
    t = time.time()
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ss-daily-check"}), timeout=timeout) as r:
        return r.status, r.read(), time.time() - t


run("git", "pull", "-q", "--rebase", "--autostash")
# the catalogue itself is kept in the catalogue-data release, not git: get the latest copy
_py = Path(ROOT) / ".venv" / "bin" / "python"
subprocess.run([str(_py) if _py.exists() else sys.executable, "-m", "scripts.catalogue_store", "fetch"], cwd=ROOT,
               capture_output=True, text=True)
print("== Site ==")
try:
    code, body, secs = get(SITE + "/")
    live = hashlib.sha1(body.decode().strip().encode()).hexdigest()
    repo = hashlib.sha1(run("git", "show", "origin/main:static/index.html").encode()).hexdigest()   # run() strips too
    print(f"  Up: HTTP {code} in {secs:.1f}s" + ("  (slow: it was asleep, free plan)" if secs > 10 else ""))
    print("  Version: " + ("latest pushed version is live" if live == repo else "live page differs from the latest push (a deploy may be stuck or still going)"))
    code, body, _ = get(SITE + "/api/stats")
    s = json.loads(body)
    print(f"  Home page data: {sum(len(g) for g in s.get('fresh_sets', []))} new releases, {len(s.get('most_played', []))} most played")
except Exception as e:
    print(f"  PROBLEM: site not answering ({e})")

print("\n== 6am track pull (GitHub Actions) ==")
try:
    _, body, _ = get(f"https://api.github.com/repos/{REPO}/actions/workflows/daily-catalogue.yml/runs?per_page=6")
    shown = 0
    for r in json.loads(body)["workflow_runs"]:
        # two wake-ups a day (05:00 and 06:00 UTC); only the one that is 6am in the UK does the work
        _, jb, _ = get(f"https://api.github.com/repos/{REPO}/actions/runs/{r['id']}/jobs")
        job = next((j for j in json.loads(jb)["jobs"] if j["name"] == "update"), None)
        if job and job["conclusion"] == "skipped":
            continue
        result = (job and (job["conclusion"] or job["status"])) or r["conclusion"] or r["status"]
        print(f"  {r['created_at'][:16].replace('T', ' ')} UTC  {r['event']:<17} {result}")
        shown += 1
        if shown == 4: break
except Exception as e:
    print(f"  couldn't read the runs ({e})")

print("\n== What it pulled in ==")
print(subprocess.run([sys.executable, "scripts/catalogue_report.py", DAYS], cwd=ROOT, capture_output=True, text=True).stdout)
