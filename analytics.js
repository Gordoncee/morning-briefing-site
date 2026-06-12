(function () {
  const config = window.MB_ANALYTICS || {};
  const statNodes = {
    totalViews: document.getElementById("stats-total-views"),
    todayViews: document.getElementById("stats-today-views"),
    activeVisitors: document.getElementById("stats-active-visitors"),
  };

  if (!config.endpoint || !config.siteId) {
    renderPublicStats(null);
    return;
  }

  const endpoint = config.endpoint.replace(/\/$/, "");
  const storageKey = "mb_visitor_id";
  const sessionKey = "mb_session_id";

  function getOrCreate(storage, key) {
    try {
      let value = storage.getItem(key);
      if (!value) {
        value = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
        storage.setItem(key, value);
      }
      return value;
    } catch {
      return "";
    }
  }

  function collect(eventName) {
    const payload = {
      siteId: config.siteId,
      event: eventName,
      path: location.pathname,
      hash: location.hash,
      title: document.title,
      referrer: document.referrer,
      visitorId: getOrCreate(localStorage, storageKey),
      sessionId: getOrCreate(sessionStorage, sessionKey),
      language: navigator.language || "",
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "",
      screen: `${screen.width}x${screen.height}`,
      viewport: `${innerWidth}x${innerHeight}`,
      ts: new Date().toISOString(),
    };

    const body = JSON.stringify(payload);
    const url = `${endpoint}/api/collect`;

    if (navigator.sendBeacon) {
      const blob = new Blob([body], { type: "application/json" });
      if (navigator.sendBeacon(url, blob)) return;
    }

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      keepalive: true,
    }).catch(() => {});
  }

  async function loadPublicStats() {
    if (!statNodes.totalViews) return;

    try {
      const params = new URLSearchParams({ siteId: config.siteId });
      const response = await fetch(`${endpoint}/api/public-stats?${params.toString()}`, {
        headers: { Accept: "application/json" },
        cache: "no-store",
      });
      if (!response.ok) throw new Error("Stats unavailable");
      renderPublicStats(await response.json());
    } catch {
      renderPublicStats(null);
    }
  }

  function renderPublicStats(stats) {
    if (!statNodes.totalViews) return;

    const values = stats
      ? {
          totalViews: stats.totalViews,
          todayViews: stats.todayViews,
          activeVisitors: stats.activeVisitors,
        }
      : {
          totalViews: "待启用",
          todayViews: "--",
          activeVisitors: "--",
        };

    statNodes.totalViews.textContent = formatStat(values.totalViews);
    statNodes.todayViews.textContent = formatStat(values.todayViews);
    statNodes.activeVisitors.textContent = formatStat(values.activeVisitors);
  }

  function formatStat(value) {
    return typeof value === "number" ? value.toLocaleString("zh-CN") : value;
  }

  collect("pageview");
  loadPublicStats();
  window.setInterval(loadPublicStats, 60000);

  let lastHash = location.hash;
  window.addEventListener("hashchange", () => {
    if (location.hash === lastHash) return;
    lastHash = location.hash;
    collect("hashchange");
  });
})();
