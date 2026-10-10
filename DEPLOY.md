# Putting SimilarSounds online (free)

Hosting: **Render** free plan → `https://similarsounds.onrender.com` (or similar if taken)
Daily new releases: **GitHub Actions** (free) updates the catalogue every morning, Render redeploys automatically.

## 1. One-time setup on your Mac

Install Apple's developer tools (this gives you `git`):

```bash
xcode-select --install
```

## 2. Put the code on GitHub

1. Make a free account at https://github.com and create a **new empty repository** called `similarsounds`
   (no README, no .gitignore, no licence).
2. In this project folder run (replace `YOUR-USERNAME`):

```bash
git init && git add . && git commit -m "SimilarSounds prototype"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/similarsounds.git
git push -u origin main
```

## 3. Deploy on Render

1. Make a free account at https://render.com and sign in with GitHub.
2. **New → Blueprint** → choose the `similarsounds` repo. Render reads `render.yaml` and sets everything up.
3. When asked for `CANONICAL_HOST`, **leave it empty** for now.
4. Wait for the first build (~5 minutes). Your site is live at the `.onrender.com` address it shows.

Free-plan notes: the site sleeps after ~15 minutes without visitors, so the first visit after that
takes ~1 minute to wake up. If it ever runs out of memory, the Starter plan ($7/month) fixes it.

## 4. Daily new releases

Nothing to do - `.github/workflows/daily-catalogue.yml` runs at 05:00 UTC every day.
To run it now: GitHub repo → **Actions** → *Daily catalogue update* → **Run workflow**.

## Later: switching to similarsounds.com

1. Buy `similarsounds.com` at any registrar.
2. Render → your service → **Settings → Custom Domains → Add** `similarsounds.com`.
3. Add the DNS records Render shows you at your registrar. HTTPS is set up automatically.
4. Render → **Environment** → set `CANONICAL_HOST` = `similarsounds.com`.
   The old `.onrender.com` address now permanently redirects to the new domain.

## Before a public launch

The stand-in preview source (Deezer) allows **non-commercial use only**: no ads, no paid features,
until Beatport (or another licensed source) replaces it.
