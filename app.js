(function () {
  const briefings = [...window.MORNING_BRIEFINGS].sort((a, b) => b.date.localeCompare(a.date));
  let openDate = window.location.hash.replace("#", "") || null;

  const latestStatus = document.getElementById("latest-status");
  const digestGrid = document.getElementById("digest-grid");

  function renderCards(scrollToOpen) {
    latestStatus.textContent = briefings[0] ? `最新：${briefings[0].displayDate}` : "等待更新";
    digestGrid.innerHTML = briefings.map((briefing, index) => {
      const topItems = briefing.items.slice(0, 3);
      const isOpen = openDate === briefing.date;
      const activeClass = isOpen ? " open" : "";
      return `
        <article class="digest-card${activeClass}" data-date="${briefing.date}">
          <button class="card-summary-button" type="button" aria-expanded="${isOpen ? "true" : "false"}">
            <span class="card-kicker">${index === 0 ? "最新简报" : "历史简报"}</span>
            <span class="card-date">${escapeHtml(briefing.displayDate)}</span>
            <span class="card-summary">${escapeHtml(briefing.summary)}</span>
            <span class="card-lines">
              ${topItems.map((item, itemIndex) => `
                <span><b>${String(itemIndex + 1).padStart(2, "0")}</b>${escapeHtml(item.title)}</span>
              `).join("")}
            </span>
            <span class="card-footer">
              <span>${briefing.items.length}条重点新闻</span>
              <span>${isOpen ? "收起详情" : "查看详情"}</span>
            </span>
          </button>
          ${isOpen ? renderExpanded(briefing) : ""}
        </article>
      `;
    }).join("");

    document.title = openDate ? `${findBriefing(openDate)?.displayDate || ""}｜晨间科技财经简报` : "晨间科技财经简报";

    if (scrollToOpen && openDate) {
      const openCard = digestGrid.querySelector(`.digest-card[data-date="${CSS.escape(openDate)}"]`);
      openCard?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function renderExpanded(briefing) {
    return `
      <div class="expanded">
        <div class="expanded-grid">
          <section class="expanded-news" aria-label="${escapeAttribute(briefing.displayDate)}五条新闻">
            <h3>完整简报</h3>
            <div class="news-list">
              ${briefing.items.map((item, index) => `
                <article class="news-item">
                  <div class="news-num">${String(index + 1).padStart(2, "0")}</div>
                  <div>
                    <h4>${escapeHtml(item.title)}</h4>
                    <p class="meta">地区/主体：${escapeHtml(item.region)}｜来源：${item.sources.map(escapeHtml).join("、")}</p>
                    <p><strong>摘要：</strong>${escapeHtml(item.summary)}</p>
                    <p><strong>关注：</strong>${escapeHtml(item.why)}</p>
                    <p><strong>观察：</strong>${escapeHtml(item.watch)}</p>
                  </div>
                </article>
              `).join("")}
            </div>
          </section>

          <aside class="expanded-side">
            <section class="focus-panel">
              <h3>今日重点关注</h3>
              <ol class="focus-list">
                ${briefing.focus.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
              </ol>
            </section>

            <section class="sources-panel">
              <h3>来源链接</h3>
              <div class="source-list">
                ${briefing.sourceLinks.map((link) => `
                  <a href="${escapeAttribute(link)}" target="_blank" rel="noreferrer">${escapeHtml(displayUrl(link))}</a>
                `).join("")}
              </div>
            </section>

            <button class="copy-button" type="button" data-copy-date="${briefing.date}">复制本期链接</button>
          </aside>
        </div>
      </div>
    `;
  }

  function displayUrl(link) {
    try {
      const url = new URL(link);
      return `${url.hostname}${url.pathname === "/" ? "" : url.pathname}`;
    } catch {
      return link;
    }
  }

  function findBriefing(date) {
    return briefings.find((item) => item.date === date);
  }

  function setHash(date) {
    if (date) {
      window.history.replaceState(null, "", `#${date}`);
    } else {
      window.history.replaceState(null, "", window.location.href.split("#")[0]);
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function escapeAttribute(value) {
    return escapeHtml(value).replaceAll("`", "&#096;");
  }

  digestGrid.addEventListener("click", async (event) => {
    const copyButton = event.target.closest("[data-copy-date]");
    if (copyButton) {
      const url = `${window.location.href.split("#")[0]}#${copyButton.dataset.copyDate}`;
      try {
        await navigator.clipboard.writeText(url);
        copyButton.textContent = "已复制";
      } catch {
        copyButton.textContent = "复制失败";
      }
      setTimeout(() => {
        copyButton.textContent = "复制本期链接";
      }, 1400);
      return;
    }

    const summaryButton = event.target.closest(".card-summary-button");
    if (!summaryButton) return;
    const card = summaryButton.closest(".digest-card");
    const nextDate = card.dataset.date;
    openDate = openDate === nextDate ? null : nextDate;
    setHash(openDate);
    renderCards(Boolean(openDate));
  });

  renderCards(Boolean(openDate));
})();
