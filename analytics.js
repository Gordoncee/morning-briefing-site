(function () {
  const config = window.MB_ANALYTICS || {};
  if (!config.endpoint || !config.siteId) return;

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

  collect("pageview");

  let lastHash = location.hash;
  window.addEventListener("hashchange", () => {
    if (location.hash === lastHash) return;
    lastHash = location.hash;
    collect("hashchange");
  });
})();
