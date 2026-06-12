CREATE TABLE IF NOT EXISTS visits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  site_id TEXT NOT NULL,
  event TEXT NOT NULL,
  path TEXT NOT NULL,
  hash TEXT DEFAULT '',
  title TEXT DEFAULT '',
  referrer TEXT DEFAULT '',
  visitor_id TEXT DEFAULT '',
  session_id TEXT DEFAULT '',
  language TEXT DEFAULT '',
  timezone TEXT DEFAULT '',
  screen TEXT DEFAULT '',
  viewport TEXT DEFAULT '',
  user_agent TEXT DEFAULT '',
  country TEXT DEFAULT '',
  ip_hash TEXT DEFAULT '',
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_visits_site_created ON visits(site_id, created_at);
CREATE INDEX IF NOT EXISTS idx_visits_site_path ON visits(site_id, path);
CREATE INDEX IF NOT EXISTS idx_visits_site_visitor ON visits(site_id, visitor_id);
