# Quote Vault

A personal PWA for saving quotes from philosophical essays and articles, searchable by mood as well as by topic. Type how you're feeling, get back the quote in your collection that actually resonates — with a one-line explanation of why.

**Live app:** https://quote-vault-rose.vercel.app
**Stack:** FastAPI (Python) · React/TypeScript (Vite) · PostgreSQL + pgvector · Google Gemini

## Why

Most quote apps are a static, scrollable list sorted by whenever you saved each one. This one leans on semantic search instead — the input is a feeling ("overwhelmed," "hopeful," "restless"), not a keyword, and the app finds the saved quote that actually fits. Saving one is meant to take no more than a paste and a tap; tagging happens automatically.

## Features

- **Mood search** — describe a feeling, get back your closest-matching saved quote plus a one-sentence explanation of why it fits
- **Quick capture** — paste a quote, save it in one tap; author auto-detected from a trailing `— Author` if present
- **Auto-tagging** — Gemini tags each quote on save, reusing existing tags instead of coining synonyms so the tag vocabulary stays tight over time
- **Tag browse** — quotes grouped by mood/theme category, not a flat list
- **Installable PWA** — offline reading of previously-viewed quotes, Android Share Target integration (share text from any app straight into Quick Capture), read-aloud via the Web Speech API
- **Graceful degradation** — if the LLM is rate-limited or unavailable, quotes still save (just untagged) and mood search still returns a match (with a template-based fallback explanation built from the quote's existing tags)

## Architecture

```
frontend/            React + TypeScript + Vite + Tailwind, deployed to Vercel
app/                  FastAPI backend, deployed to Render
  routers/            quotes.py (CRUD + tags), search.py (topic/mood search)
  embeddings.py       Local embedding model (fastembed / ONNX Runtime — not
                      PyTorch, which OOMs on memory-constrained hosts)
  tagging.py          Gemini calls: auto-tagging, mood explanations, fallbacks
  rate_limit.py       Owner-only write access + spoofing-resistant public rate limit
db/init.sql           Postgres schema (pgvector, no ANN index — brute-force
                      cosine is fast enough at personal scale)
```

Search ranks quotes with pgvector cosine similarity in a single SQL statement, with tag filtering folded into the same query. The LLM never sits in the search path — Gemini is only called on save (to tag) and after a mood match is found (to explain), so search itself stays fast and never blocks on the LLM.

## Running locally

**Backend**
```bash
docker compose up -d          # Postgres + pgvector
cp .env.example .env          # fill in GEMINI_API_KEY
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
cp .env.example .env          # VITE_API_BASE_URL=http://localhost:8000
npm install
npm run dev
```

**Tests**
```bash
pytest          # 37 tests: search ranking, embedding pipeline, tagging, rate limiting
ruff check .
```

## Deployment

- **Frontend** → Vercel (static build, auto-deploys on push)
- **Backend** → Render (Python web service, auto-deploys on push)
- **Database** → Neon Postgres (pgvector extension), pooled connection for cold-start safety

This deployment is public and rate-limited: anyone can try mood and topic search, but saving new quotes is restricted to the app owner via a constant-time-compared access key, and public traffic is capped at a few requests/day per IP to protect the LLM API quota from abuse. See `app/rate_limit.py`.

## License

Personal project, shared for portfolio purposes.
