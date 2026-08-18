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

-- No ANN index (ivfflat/hnsw) by design — see CLAUDE.md: at this scale,
-- brute-force cosine over <=> is fast enough, and ivfflat built before rows
-- exist produces degenerate clusters that make search miss real matches.
