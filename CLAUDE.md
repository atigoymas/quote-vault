# Quote Vault

A personal PWA for saving quotes from philosophical essays, searchable by topic
and by mood. Single user, personal scale (hundreds to low thousands of quotes).

## Stack

- FastAPI, async throughout (asyncpg)
- Postgres + pgvector, hosted on Neon
- Embeddings: sentence-transformers `all-MiniLM-L6-v2`, 384-dim, run locally
- LLM (Claude or OpenAI): auto-tagging and the "why this resonates" line only
- Frontend: React + Tailwind + Vite, installable PWA

## Decisions — do not relitigate these

- **pgvector, not a dedicated vector DB.** Filtering by tag and ranking by
  similarity must happen in a single SQL statement. At this scale brute-force
  cosine is fast enough; ANN indexing is not needed.
- **Embeddings run locally, not via API.** No per-quote cost, no network hop on save.
- **LLM is not in the search path.** Search is pure vector similarity. The LLM only
  generates tags on save and one explanation sentence on a mood hit. Keep search fast.
- **Mood search is the primary screen**, not a secondary tab. It is the reason the
  app exists.
- **No OCR, no image storage.** Quotes are plain text only.

## Conventions

- Pydantic models for every request and response shape
- `ruff` clean before commit
- pytest coverage required for search ranking logic and the embedding pipeline
- `.env.example` committed, real `.env` never
- Local dev runs against docker-compose Postgres with the pgvector image
- Production is Neon. Use the pooled connection string, not the direct one —
  Neon scales to zero, so connections must survive cold starts. Enable pgvector
  with `CREATE EXTENSION IF NOT EXISTS vector;` on first migration.

## Git

- Never add Claude as a co-author. No `Co-Authored-By` trailers.
- Never mention Claude, Claude Code, or AI assistance in commit messages, PR
  descriptions, or code comments.
- Commit messages describe the change and why, in the imperative mood.

## Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE quotes (
    id          SERIAL PRIMARY KEY,
    text        TEXT NOT NULL,
    source      TEXT,
    author      TEXT,
    tags        TEXT[],
    embedding   VECTOR(384),
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ON quotes USING ivfflat (embedding vector_cosine_ops);
```

Search shape — tag filter and similarity ranking in one statement:

```sql
SELECT id, text, source, tags,
       1 - (embedding <=> :query_embedding) AS similarity
FROM quotes
WHERE (:tag IS NULL OR :tag = ANY(tags))
ORDER BY embedding <=> :query_embedding
LIMIT 5;
```

## API surface

```
POST   /quotes           save → embed → auto-tag → store
GET    /quotes           paginated, optional ?tag=
GET    /quotes/{id}
DELETE /quotes/{id}
POST   /search/topic     { query }   → similar quotes
POST   /search/mood      { feeling } → best match + one-line explanation
GET    /tags             distinct tags with counts
```

## Design direction

The quotes are the content, so they should look like the point of the app. One
characterful serif for quote text with generous line-height and a narrow measure;
one quiet sans for UI chrome. The mood input is the signature element — a single
wide field, first thing on open. Everything else stays quieter than it.

Avoid: equal-weight card grids, dashboard chrome, and the cream-plus-terracotta
palette that every generated app defaults to.