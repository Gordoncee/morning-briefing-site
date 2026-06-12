const JSON_HEADERS = {
  "Content-Type": "application/json; charset=utf-8",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: JSON_HEADERS });
    }

    if (url.pathname === "/api/collect" && request.method === "POST") {
      return collect(request, env);
    }

    if (url.pathname === "/api/public-stats" && request.method === "GET") {
      return publicStats(request, env);
    }

    if (url.pathname === "/api/stats" && request.method === "GET") {
      return stats(request, env);
    }

    if (url.pathname === "/health") {
      return json({ ok: true, service: "morning-briefing-analytics" });
    }

    return json({ error: "Not found" }, 404);
  },
};

async function collect(request, env) {
  const body = await request.json().catch(() => null);
  if (!body || body.siteId !== env.SITE_ID) {
    return json({ ok: false }, 400);
  }

  const cf = request.cf || {};
  const ip = request.headers.get("CF-Connecting-IP") || "";
  const userAgent = request.headers.get("User-Agent") || "";
  const now = new Date().toISOString();
  const ipHash = await sha256(`${env.IP_HASH_SALT || ""}:${ip}`);

  const safe = {
    siteId: clip(body.siteId, 80),
    event: clip(body.event || "pageview", 40),
    path: clip(body.path || "/", 300),
    hash: clip(body.hash || "", 200),
    title: clip(body.title || "", 300),
    referrer: clip(body.referrer || "", 500),
    visitorId: clip(body.visitorId || "", 80),
    sessionId: clip(body.sessionId || "", 80),
    language: clip(body.language || "", 40),
    timezone: clip(body.timezone || "", 80),
    screen: clip(body.screen || "", 40),
    viewport: clip(body.viewport || "", 40),
    userAgent: clip(userAgent, 500),
    country: clip(cf.country || "", 8),
    ipHash,
    createdAt: now,
  };

  await env.DB.prepare(`
    INSERT INTO visits (
      site_id, event, path, hash, title, referrer, visitor_id, session_id,
      language, timezone, screen, viewport, user_agent, country, ip_hash, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    safe.siteId, safe.event, safe.path, safe.hash, safe.title, safe.referrer,
    safe.visitorId, safe.sessionId, safe.language, safe.timezone, safe.screen,
    safe.viewport, safe.userAgent, safe.country, safe.ipHash, safe.createdAt
  ).run();

  return json({ ok: true });
}

async function stats(request, env) {
  const token = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  if (!env.ADMIN_TOKEN || token !== env.ADMIN_TOKEN) {
    return json({ error: "Unauthorized" }, 401);
  }

  const url = new URL(request.url);
  const siteId = url.searchParams.get("siteId") || env.SITE_ID;
  const days = Math.min(90, Math.max(1, Number(url.searchParams.get("days") || 30)));

  const [totals, daily, topPages, topReferrers, topCountries, recent] = await Promise.all([
    getTotals(env.DB, siteId),
    all(env.DB, `
      SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS views, COUNT(DISTINCT visitor_id) AS visitors
      FROM visits
      WHERE site_id = ? AND created_at >= datetime('now', ?)
      GROUP BY day
      ORDER BY day ASC
    `, siteId, `-${days} days`),
    all(env.DB, `
      SELECT path || COALESCE(hash, '') AS path, COUNT(*) AS views, COUNT(DISTINCT visitor_id) AS visitors
      FROM visits
      WHERE site_id = ? AND created_at >= datetime('now', ?)
      GROUP BY path
      ORDER BY views DESC
      LIMIT 10
    `, siteId, `-${days} days`),
    all(env.DB, `
      SELECT CASE WHEN referrer = '' THEN '直接访问' ELSE referrer END AS referrer,
             COUNT(*) AS views, COUNT(DISTINCT visitor_id) AS visitors
      FROM visits
      WHERE site_id = ? AND created_at >= datetime('now', ?)
      GROUP BY referrer
      ORDER BY views DESC
      LIMIT 10
    `, siteId, `-${days} days`),
    all(env.DB, `
      SELECT CASE WHEN country = '' THEN '未知' ELSE country END AS country,
             COUNT(*) AS views, COUNT(DISTINCT visitor_id) AS visitors
      FROM visits
      WHERE site_id = ? AND created_at >= datetime('now', ?)
      GROUP BY country
      ORDER BY views DESC
      LIMIT 10
    `, siteId, `-${days} days`),
    all(env.DB, `
      SELECT created_at, event, path, hash, country
      FROM visits
      WHERE site_id = ?
      ORDER BY created_at DESC
      LIMIT 30
    `, siteId),
  ]);

  return json({ totals, daily, topPages, topReferrers, topCountries, recent });
}

async function publicStats(request, env) {
  const url = new URL(request.url);
  const siteId = url.searchParams.get("siteId") || env.SITE_ID;
  if (siteId !== env.SITE_ID) {
    return json({ error: "Unknown site" }, 404);
  }

  const row = await env.DB.prepare(`
    SELECT
      COUNT(CASE WHEN event = 'pageview' THEN 1 END) AS totalViews,
      COUNT(DISTINCT CASE WHEN event = 'pageview' THEN visitor_id END) AS totalVisitors,
      SUM(CASE WHEN event = 'pageview' AND substr(created_at, 1, 10) = substr(datetime('now'), 1, 10) THEN 1 ELSE 0 END) AS todayViews,
      COUNT(DISTINCT CASE WHEN created_at >= datetime('now', '-15 minutes') THEN visitor_id END) AS activeVisitors
    FROM visits
    WHERE site_id = ?
  `).bind(siteId).first();

  return json({
    totalViews: row?.totalViews || 0,
    totalVisitors: row?.totalVisitors || 0,
    todayViews: row?.todayViews || 0,
    activeVisitors: row?.activeVisitors || 0,
    activeWindowMinutes: 15,
    updatedAt: new Date().toISOString(),
  });
}

async function getTotals(db, siteId) {
  const row = await db.prepare(`
    SELECT
      SUM(CASE WHEN substr(created_at, 1, 10) = substr(datetime('now'), 1, 10) THEN 1 ELSE 0 END) AS viewsToday,
      COUNT(DISTINCT CASE WHEN substr(created_at, 1, 10) = substr(datetime('now'), 1, 10) THEN visitor_id END) AS visitorsToday,
      SUM(CASE WHEN created_at >= datetime('now', '-24 hours') THEN 1 ELSE 0 END) AS views24h,
      SUM(CASE WHEN created_at >= datetime('now', '-7 days') THEN 1 ELSE 0 END) AS views7d
    FROM visits
    WHERE site_id = ?
  `).bind(siteId).first();
  return {
    viewsToday: row?.viewsToday || 0,
    visitorsToday: row?.visitorsToday || 0,
    views24h: row?.views24h || 0,
    views7d: row?.views7d || 0,
  };
}

async function all(db, sql, ...params) {
  const result = await db.prepare(sql).bind(...params).all();
  return result.results || [];
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: JSON_HEADERS });
}

function clip(value, max) {
  return String(value || "").slice(0, max);
}

async function sha256(text) {
  const input = new TextEncoder().encode(text);
  const hash = await crypto.subtle.digest("SHA-256", input);
  return [...new Uint8Array(hash)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}
