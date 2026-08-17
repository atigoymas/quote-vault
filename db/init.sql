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
