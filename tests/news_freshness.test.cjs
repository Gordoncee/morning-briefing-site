const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../site/assets/news-freshness.js'), 'utf8');
const oldVersion = 'a'.repeat(64);
const newVersion = 'b'.repeat(64);
const status = (latest = '2026-11-02', archive_sha256 = newVersion) => ({schema_version: 1, latest, archive_sha256});
const settle = () => new Promise(resolve => setImmediate(resolve));

function browser(options = {}) {
  let now = 1000000;
  let next = options.next || status();
  let reloads = 0;
  const requests = [], events = {}, intervals = [], notices = [];
  const storage = options.storage || new Map();
  const archive = {prepend: node => notices.push(node)};
  const search = {value: options.search || ''};
  const document = {
    visibilityState: options.hidden ? 'hidden' : 'visible',
    activeElement: {tagName: options.typing ? 'INPUT' : 'BODY'},
    getElementById: id => id === 'news-archive' ? (options.detail ? null : archive) : search,
    createElement: () => ({setAttribute() {}}),
    querySelector: selector => ({
      'meta[name="news-archive-version"]': {content: options.version || oldVersion},
      'meta[name="news-latest-date"]': {content: options.latest || '2026-10-29'},
      'link[rel="canonical"]': {href: 'https://fazhi.cc/news/'},
      '[data-news-month][aria-pressed="true"]': {dataset: {newsMonth: options.month || ''}},
    })[selector],
    addEventListener: (name, fn) => events[name] = fn,
  };
  const window = {
    location: {href: 'https://fazhi.cc/news/?v=20261026-domain', origin: 'https://fazhi.cc', reload: () => reloads++},
    sessionStorage: {
      getItem: key => {if (options.storageBlocked) throw Error('blocked'); return storage.get(key);},
      setItem: (key, value) => storage.set(key, value),
    },
    addEventListener: (name, fn) => events[name] = fn,
    setInterval: (fn, ms) => intervals.push({fn, ms}),
    setTimeout: () => 1, clearTimeout() {},
  };
  const fetch = async (url, init) => {
    requests.push({url, init});
    if (options.fetch) return options.fetch(url, init);
    if (next instanceof Error) throw next;
    return {ok: true, text: async () => JSON.stringify(next)};
  };
  vm.runInNewContext(source, {document, window, URL, AbortController, fetch, Date: {now: () => now}});
  return {document, events, requests, intervals, notices, storage, search,
    reloads: () => reloads, advance: ms => now += ms, next: value => next = value};
}

test('Oct 29 retained library detects Nov 2 and reloads without a model or full-page poll', async () => {
  const b = browser(); await settle();
  assert.equal(b.reloads(), 1);
  assert.equal(b.requests.length, 1);
  assert.equal(b.requests[0].url, 'https://fazhi.cc/news/data/news-status.json');
  assert.equal(b.requests[0].init.credentials, 'omit');
  assert.equal(b.requests[0].init.cache, 'no-store');
});
test('current archive and an older cached manifest do not reload', async () => {
  for (const next of [status('2026-11-02', oldVersion), status('2026-11-01')]) {
    const b = browser({latest: '2026-11-02', next}); await settle();
    assert.equal(b.reloads(), 0); assert.equal(b.notices.length, 0);
  }
});
test('returning to a frozen tab and visibility changes check a newer issue', async () => {
  const b = browser({next: status('2026-10-29', oldVersion)}); await settle();
  b.advance(6 * 60000); b.next(status()); b.events.pageshow({persisted: true}); await settle();
  assert.equal(b.reloads(), 1);
  const hidden = browser({hidden: true}); await settle();
  assert.equal(hidden.requests.length, 0);
  hidden.document.visibilityState = 'visible'; hidden.events.visibilitychange(); await settle();
  assert.equal(hidden.reloads(), 1);
});
test('five-minute polling is quiet while the tab is hidden and resumes on focus', async () => {
  const b = browser({hidden: true});
  assert.equal(b.intervals[0].ms, 300000);
  await b.intervals[0].fn(); assert.equal(b.requests.length, 0);
  b.document.visibilityState = 'visible'; b.events.focus(); await settle();
  assert.equal(b.requests.length, 1);
});
test('rapid focus/pageshow events coalesce a pending fetch', async () => {
  let finish;
  const b = browser({fetch: () => new Promise(resolve => finish = resolve)});
  b.events.focus(); b.events.pageshow({persisted: true});
  assert.equal(b.requests.length, 1);
  finish({ok: true, text: async () => JSON.stringify(status())}); await settle();
  assert.equal(b.reloads(), 1);
});
test('typed searches, selected months and focused form fields survive an update', async () => {
  for (const options of [{search: '2026-10-30'}, {month: '2026-10'}, {typing: true}]) {
    const b = browser(options); await settle();
    assert.equal(b.reloads(), 0); assert.equal(b.notices.length, 1);
    assert.match(b.notices[0].textContent, /2026-11-02/);
    assert.equal(new URL(b.notices[0].href).searchParams.get('news_version'), newVersion.slice(0, 12));
    assert.equal(b.search.value, options.search || '');
  }
});
test('a stale response after reload cannot cause a loop', async () => {
  const b = browser(); await settle(); assert.equal(b.reloads(), 1);
  const restored = browser({storage: b.storage}); await settle();
  assert.equal(restored.reloads(), 0); assert.equal(restored.notices.length, 1);
});
test('blocked browser storage leaves an explicit update link rather than reloading', async () => {
  const b = browser({storageBlocked: true}); await settle();
  assert.equal(b.reloads(), 0); assert.equal(b.notices.length, 1);
});
test('historical dated issue pages are never replaced by the newest issue', async () => {
  const b = browser({detail: true}); await settle();
  assert.equal(b.requests.length, 0); assert.equal(b.reloads(), 0);
});
test('network errors retain readable content and a later check can recover', async () => {
  const b = browser({next: Error('network')}); await settle();
  assert.equal(b.reloads(), 0); assert.equal(b.notices.length, 0);
  b.next(status()); b.advance(300000); await b.intervals[0].fn();
  assert.equal(b.reloads(), 1);
});
test('untrusted or malformed status cannot trigger a reload or enter the DOM', async () => {
  for (const next of [status('javascript:alert(1)'), status('2026-11-02', '<script>'), {...status(), schema_version: 2}]) {
    const b = browser({next}); await settle();
    assert.equal(b.reloads(), 0); assert.equal(b.notices.length, 0);
  }
});
