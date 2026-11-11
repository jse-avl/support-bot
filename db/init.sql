-- n8n keeps its own tables in the "n8n" schema; the bot's data lives in "bot".
CREATE SCHEMA IF NOT EXISTS n8n;
CREATE SCHEMA IF NOT EXISTS bot;
CREATE EXTENSION IF NOT EXISTS vector;

-- Knowledge base chunks (filled by the ingest workflow).
CREATE TABLE bot.kb_chunks (
  id          BIGSERIAL PRIMARY KEY,
  source      TEXT NOT NULL,          -- file name, e.g. "envios.md"
  heading     TEXT,                   -- section title, used in citations
  content     TEXT NOT NULL,
  tsv         TSVECTOR GENERATED ALWAYS AS (to_tsvector('spanish', coalesce(heading,'') || ' ' || content)) STORED,
  embedding   VECTOR(768) ,           -- optional; NULL when running keyword-only
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX kb_chunks_tsv_idx ON bot.kb_chunks USING GIN (tsv);

-- Every bot turn, for metrics (handle rate, escalations, latency).
CREATE TABLE bot.messages (
  id            BIGSERIAL PRIMARY KEY,
  session_id    TEXT NOT NULL,
  role          TEXT NOT NULL CHECK (role IN ('user','assistant')),
  content       TEXT NOT NULL,
  sources       TEXT[],
  resolved      BOOLEAN,              -- bot's own judgement for assistant turns
  latency_ms    INTEGER,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX messages_session_idx ON bot.messages (session_id, created_at);

-- Hand-offs to a human agent.
CREATE TABLE bot.escalations (
  id          BIGSERIAL PRIMARY KEY,
  session_id  TEXT NOT NULL,
  reason      TEXT NOT NULL,          -- 'user_requested' | 'unresolved_twice' | 'sensitive'
  summary     TEXT,
  status      TEXT NOT NULL DEFAULT 'open',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Daily KPIs: how many sessions the bot handled without a human (handle rate), latency.
CREATE OR REPLACE VIEW bot.metrics_daily AS
WITH s AS (
  SELECT date_trunc('day', m.created_at)::date AS day, m.session_id,
         bool_or(e.id IS NOT NULL) AS escalated
  FROM bot.messages m
  LEFT JOIN bot.escalations e ON e.session_id = m.session_id
  GROUP BY 1, 2
)
SELECT s.day,
       count(*)                                              AS sessions,
       count(*) FILTER (WHERE NOT s.escalated)               AS handled_by_bot,
       round(100.0 * count(*) FILTER (WHERE NOT s.escalated) / count(*), 1) AS handle_rate_pct,
       (SELECT count(*) FROM bot.messages a WHERE a.role = 'assistant' AND a.created_at::date = s.day) AS bot_answers,
       (SELECT round(avg(latency_ms)) FROM bot.messages a WHERE a.role = 'assistant' AND a.created_at::date = s.day) AS avg_latency_ms,
       (SELECT percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) FROM bot.messages a
         WHERE a.role = 'assistant' AND a.created_at::date = s.day) AS p95_latency_ms
FROM s GROUP BY s.day ORDER BY s.day DESC;
