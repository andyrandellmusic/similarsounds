# Putting SimilarSounds online (free)

Live at **https://www.similarsounds.com** (Render free plan, also reachable at `similarsounds.onrender.com`)
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

## Custom domain (done: www.similarsounds.com)

- Namecheap → Advanced DNS host records:
  - `A` record, host `@` → `216.24.57.1` (Render)
  - `CNAME` record, host `www` → `similarsounds.onrender.com`
- Render → Settings → Custom Domains: `similarsounds.com` (redirects to www) and `www.similarsounds.com`.
- Render → Environment: `CANONICAL_HOST` = `www.similarsounds.com`, so the `.onrender.com`
  address permanently redirects to the main address.
- Keep `CANONICAL_HOST` matching the domain Render treats as primary (`www...`), otherwise the
  two redirects send visitors back and forth.

## Before a public launch

The stand-in preview source (Deezer) allows **non-commercial use only**: no ads, no paid features,
until Beatport (or another licensed source) replaces it.

## SimilarSounds Unlimited (£4.99 / month) - built, switched OFF

Everything is in place (`app/billing.py`, the Go Unlimited button, Manage subscription in the account) but the
site keeps showing "Subscriptions coming soon" until it's switched on. **Only switch it on once Deezer (or
Beatport / another licensed source) has agreed to paid use** - see "Before a public launch" above.

To switch on:
1. **Stripe** (stripe.com): create the product "SimilarSounds Unlimited" with a £4.99 / month recurring price.
   Copy its price id (`price_...`).
2. Stripe → Developers → Webhooks → add endpoint `https://www.similarsounds.com/api/stripe/webhook` with the events
   `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`,
   `customer.subscription.deleted`. Copy its signing secret (`whsec_...`).
3. Stripe → Settings → Billing → Customer portal: turn it on (lets subscribers cancel or change their card).
4. Supabase → Project settings → API: copy the `service_role` key (keep it secret: server only).
5. Render → similarsounds → Environment, add:
   `STRIPE_SECRET_KEY`, `STRIPE_PRICE_ID`, `STRIPE_WEBHOOK_SECRET`, `SUPABASE_SERVICE_KEY`, and `SUBSCRIPTIONS_ON` = `1`.
   Render redeploys; the pop-up then shows **Go Unlimited · £4.99/month**.
6. Update the Terms page with the subscription terms (price, renews monthly, cancel anytime, UK 14-day cancellation
   rights) before taking real payments. Try it first with Stripe's test keys and card 4242 4242 4242 4242.

A paying account gets a row in `public.subscriptions` (status active), which the search_tokens function already
treats as unlimited. Free users keep their searches refreshing every 24 hours. The owner row (`customer_ref`
starting with `owner`) is never changed by payments.
