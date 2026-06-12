(function () {
  const config = window.MB_ANALYTICS || {};
  const apiInput = document.getElementById("api-base");
  const tokenInput = document.getElementById("admin-token");
  const saveButton = document.getElementById("save-config");
  const refreshButton = document.getElementById("refresh");

  apiInput.value = sessionStorage.getItem("mb_admin_api") || config.endpoint || "";
  tokenInput.value = sessionStorage.getItem("mb_admin_token") || "";

  function setText(id, value) {
    document.getElementById(id).textContent = value ?? "-";
  }

  function getApiBase() {
    return apiInput.value.trim().replace(/\/$/, "");
  }

  function getToken() {
    return tokenInput.value.trim();
  }

  async function loadStats() {
    const apiBase = getApiBase();
    const token = getToken();
    if (!apiBase || !token) return;

    sessionStorage.setItem("mb_admin_api", apiBase);
    sessionStorage.setItem("mb_admin_token", token);

    const response = await fetch(`${apiBase}/api/stats?siteId=morning-briefing-site&days=30`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!response.ok) {
      throw new Error(`统计接口返回 ${response.status}`);
    }
    const data = await response.json();
    render(data);
  }

  function render(data) {
    setText("views-today", data.totals?.viewsToday || 0);
    setText("visitors-today", data.totals?.visitorsToday || 0);
    setText("views-24h", data.totals?.views24h || 0);
    setText("views-7d", data.totals?.views7d || 0);
    renderDaily(data.daily || []);
    renderRows("top-pages", data.topPages || [], "path");
    renderRows("top-referrers", data.topReferrers || [], "referrer");
    renderRows("top-countries", data.topCountries || [], "country");
    renderRecent(data.recent || []);
  }

  function renderDaily(rows) {
    const max = Math.max(1, ...rows.map((row) => row.views));
    document.getElementById("daily-chart").innerHTML = rows.map((row) => `
      <div class="bar-row">
        <span>${escapeHtml(row.day)}</span>
        <span class="bar-track"><span class="bar-fill" style="width:${Math.max(2, row.views / max * 100)}%"></span></span>
        <b>${row.views}</b>
      </div>
    `).join("");
  }

  function renderRows(id, rows, labelKey) {
    const target = document.getElementById(id);
    target.innerHTML = rows.length ? rows.map((row) => `
      <div class="table-row">
        <b>${escapeHtml(row[labelKey] || "直接访问")}</b>
        <span>${row.views} 次 / ${row.visitors || 0} 人</span>
      </div>
    `).join("") : `<p class="muted">暂无数据</p>`;
  }

  function renderRecent(rows) {
    const target = document.getElementById("recent");
    target.innerHTML = rows.length ? rows.map((row) => `
      <div class="table-row">
        <span>${escapeHtml(row.created_at)}</span>
        <b>${escapeHtml(row.path || "/")}${escapeHtml(row.hash || "")}</b>
        <span>${escapeHtml(row.country || "未知")}</span>
        <span>${escapeHtml(row.event || "view")}</span>
      </div>
    `).join("") : `<p class="muted">暂无实时访问</p>`;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  saveButton.addEventListener("click", () => {
    loadStats().catch((error) => alert(error.message));
  });
  refreshButton.addEventListener("click", () => {
    loadStats().catch((error) => alert(error.message));
  });

  if (apiInput.value && tokenInput.value) {
    loadStats().catch(() => {});
  }
})();
