### Web (Next.js) App

Environment variables:
- `OPENAI_API_KEY`: server-only key for OpenAI. If omitted, a fallback heuristic summary is used.
- `NEXT_PUBLIC_FEED_URL`: public URL to `feed.json` on GitHub Pages.

ISR:
- The API route `/api/analysis` caches the analysis for 1 hour by default (revalidate: 3600). You can switch to 4 hours by changing `revalidate` to 14400.

Development:
- Copy `.env.example` to `.env.local` and set variables
- `npm install`
- `npm run dev`

Deploy (Vercel):
- Set `OPENAI_API_KEY` and `NEXT_PUBLIC_FEED_URL` in Vercel project settings
- Push to `main`; Vercel builds and serves ISR-cached responses from its CDN 