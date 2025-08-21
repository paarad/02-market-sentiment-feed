### PRP — Crypto‑First Market Sentiment Feed

Monorepo with a Python analyzer (publishes `public/feed.json` via GitHub Actions) and a Next.js app (ISR + OpenAI analysis). Free to run: no DBs, static feed on GitHub Pages, ISR cache on Vercel.

Constants (use across files):
- `GITHUB_USERNAME = "<YOUR_GITHUB_USERNAME>"`
- `REPO_NAME = "<YOUR_REPO_NAME>"` (e.g., `market-sentiment-feed`)
- `PAGES_FEED_URL = "https://<YOUR_GITHUB_USERNAME>.github.io/<YOUR_REPO_NAME>/feed.json"`
- Default cadence: hourly (commented 4‑hour option available)

#### Layout
- Python analyzer: `analyzer/` + `cli.py`
- Spec docs: `spec/`
- Public artifacts: `public/feed.json`, `public/history.json`
- GitHub Actions workflow: `.github/workflows/publish.yml`
- Next.js app (ISR): `web/`

#### JSON schema v1
See `spec/JSON_SCHEMA.md`.

#### Python analyzer
- Sources: CryptoPanic (optional) + CoinDesk, CoinTelegraph, Reuters Markets
- Sentiment: rule-based with crypto lexicon adjustments, outputs s ∈ [-1,1] → [0,1]
- Weighting: half-life 6h; source weights {1.0 major, 0.8 mid, 0.5 social}; +20% if cashtag/contract
- Combined: 0.9×crypto + 0.1×global
- Confidence: `sqrt(Σw/(Σw+k))` with `k=10`, scaled by source diversity
- Drivers: top 3 positive/negative by s×w
- Resilience: retries, dedupe, offline sample, keep last snapshot

Run locally:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python cli.py --window 1h --offline
```

CLI contract:
```bash
python cli.py --window 1h    # default
python cli.py --window 4h
python cli.py --offline      # bundled sample data
```

Secrets (Python):
- `CRYPTOPANIC_TOKEN` (optional)

#### GitHub Actions (publish feed)
- Triggers: manual `workflow_dispatch` and hourly cron `0 * * * *` (4‑hour option commented)
- Steps: checkout → setup Python 3.11 → install → `python cli.py --window 1h` → commit `public/`
- Keeps previous `feed.json` if fetch fails (no deletion)

First manual run:
1. Push repo to GitHub
2. In Actions, run “Publish Sentiment Feed” → confirm `public/feed.json` committed

#### GitHub Pages
- Settings → Pages → Deploy from Branch → Branch: `main`, Folder: `/` (root)
- Feed URL: `PAGES_FEED_URL` above

#### Next.js app (Vercel)
- Set env vars in Vercel:
  - `OPENAI_API_KEY` (server-only)
  - `NEXT_PUBLIC_FEED_URL = PAGES_FEED_URL`
- ISR caching window: 1h (change to 4h in `web/app/api/analysis/route.ts`)
- Deploy: `cd web && npm i && npm run build && npm start` (local) or connect to Vercel

UI displays:
- Combined/Crypto/Global gauges, confidence, last updated time
- Sparkline from history
- Top positive/negative drivers with links and source badges
- “Using cached analysis” badge; “Stale source” warning if feed is older than expected

Switch cadence to 4h:
- Uncomment `cron: '0 */4 * * *'` in workflow
- Optionally set `export const revalidate = 14400` in the API route

Rollback:
- Revert the latest commit that updated `public/feed.json`

Troubleshooting:
- Feed missing: check Actions logs; ensure Pages is enabled from root
- OpenAI errors: API route returns fallback analysis; verify `OPENAI_API_KEY`
- Stale badge: means feed `updated_at` is older than the ISR expectation 