(() => {
  'use strict';
  const archive = document.getElementById('news-archive');
  // A dated issue remains a dated issue; only the library needs live freshness.
  if (!archive) return;
  const version = document.querySelector('meta[name="news-archive-version"]')?.content;
  const latest = document.querySelector('meta[name="news-latest-date"]')?.content;
  const canonical = document.querySelector('link[rel="canonical"]')?.href;
  if (!/^[a-f0-9]{64}$/.test(version || '') || !/^\d{4}-\d{2}-\d{2}$/.test(latest || '') || !canonical) return;
  const home = new URL(canonical, window.location.href);
  if (home.origin !== window.location.origin || !home.pathname.endsWith('/')) return;
  const statusUrl = new URL('data/news-status.json', home);
  const storageKey = `fazhi-news-refreshed:${home.pathname}`;
  let lastCheck = -Infinity;
  let activeRequest = null;
  let notice;

  const offerUpdate = next => {
    if (!notice) {
      notice = document.createElement('a');
      notice.className = 'news-read-link';
      notice.id = 'news-freshness-update';
      notice.setAttribute('aria-live', 'polite');
      archive.prepend(notice);
    }
    const url = new URL(window.location.href);
    // A stable content version also gives an explicit escape from an old cache.
    url.searchParams.set('news_version', next.archive_sha256.slice(0, 12));
    notice.href = url.href;
    notice.textContent = `资讯已更新（${next.latest}），点击查看`;
  };

  const check = async () => {
    if (document.visibilityState !== 'visible' || activeRequest || Date.now() - lastCheck < 60000) return;
    lastCheck = Date.now();
    const controller = new AbortController();
    activeRequest = controller;
    const timeout = window.setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(statusUrl.href, {
        cache: 'no-store', credentials: 'omit', redirect: 'error',
        headers: {Accept: 'application/json'}, signal: controller.signal,
      });
      if (!response.ok) return;
      const text = await response.text();
      if (text.length > 4096) return;
      const next = JSON.parse(text);
      if (next.schema_version !== 1 || !/^[a-f0-9]{64}$/.test(next.archive_sha256 || '') ||
          !/^\d{4}-\d{2}-\d{2}$/.test(next.latest || '') || next.latest < latest ||
          next.archive_sha256 === version) return;
      const search = document.getElementById('news-search');
      const selected = document.querySelector('[data-news-month][aria-pressed="true"]');
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || '');
      if (search?.value.trim() || selected?.dataset.newsMonth || typing) {
        offerUpdate(next);
        return;
      }
      // Persist the target before reloading. A stale upstream or disabled
      // sessionStorage must never trap the reader in an automatic reload loop.
      try {
        if (window.sessionStorage.getItem(storageKey) === next.archive_sha256) {
          offerUpdate(next);
          return;
        }
        window.sessionStorage.setItem(storageKey, next.archive_sha256);
      } catch (error) {
        offerUpdate(next);
        return;
      }
      window.location.reload();
    } catch (error) {
      // Network failure keeps the readable page intact; retry when visible later.
    } finally {
      window.clearTimeout(timeout);
      if (activeRequest === controller) activeRequest = null;
    }
  };

  window.addEventListener('pageshow', check);
  window.addEventListener('focus', check);
  document.addEventListener('visibilitychange', check);
  window.addEventListener('pagehide', () => {
    activeRequest?.abort();
    activeRequest = null;
  });
  // Hidden/frozen tabs make no network requests; active tabs read a tiny JSON.
  window.setInterval(check, 300000);
  check();
})();
