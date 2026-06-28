(function () {
  const SITE_URL = "https://gordoncee.github.io/morning-briefing-site/";
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

            <div class="share-actions">
              <button class="share-button primary" type="button" data-export-date="${briefing.date}">下载分享图</button>
              <button class="share-button" type="button" data-copy-date="${briefing.date}">复制本期链接</button>
            </div>
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
    const exportButton = event.target.closest("[data-export-date]");
    if (exportButton) {
      const briefing = findBriefing(exportButton.dataset.exportDate);
      if (!briefing) return;

      exportButton.textContent = "正在生成";
      exportButton.disabled = true;
      try {
        await exportShareImage(briefing);
        exportButton.textContent = "已下载";
      } catch {
        exportButton.textContent = "导出失败";
      }
      setTimeout(() => {
        exportButton.textContent = "下载分享图";
        exportButton.disabled = false;
      }, 1600);
      return;
    }

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

  function exportShareImage(briefing) {
    return new Promise((resolve, reject) => {
      try {
        const canvas = renderShareCanvas(briefing);
        canvas.toBlob((blob) => {
          if (!blob) {
            reject(new Error("Export failed"));
            return;
          }
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = `morning-briefing-${briefing.date}-share.png`;
          document.body.appendChild(link);
          link.click();
          link.remove();
          URL.revokeObjectURL(link.href);
          resolve();
        }, "image/png");
      } catch (error) {
        reject(error);
      }
    });
  }

  function renderShareCanvas(briefing) {
    const palette = {
      bg: "#f5f5f7",
      paper: "#ffffff",
      ink: "#1d1d1f",
      muted: "#6e6e73",
      blue: "#0071e3",
      blueSoft: "#eaf3ff",
      line: "rgba(0, 0, 0, 0.12)",
      softLine: "rgba(0, 0, 0, 0.07)",
      panel: "#f8f8fb",
    };
    const width = 1242;
    const margin = 72;
    const pad = 86;
    const contentWidth = width - margin * 2 - pad * 2;
    const fonts = {
      kicker: font(25, 700),
      hero: font(70, 800),
      summary: font(29, 500),
      title: font(38, 760),
      meta: font(23, 500),
      label: font(23, 760),
      body: font(28, 480),
      focusTitle: font(34, 760),
      footer: font(23, 520),
      footerBold: font(24, 740),
      number: font(26, 760),
    };

    const measureCanvas = document.createElement("canvas");
    measureCanvas.width = width;
    measureCanvas.height = 100;
    const measureCtx = measureCanvas.getContext("2d");
    const dateLine = `Morning Briefing · ${briefing.date.replaceAll("-", ".")}`;
    const headline = "晨间科技财经简报";
    const websiteLine = `${SITE_URL}#${briefing.date}`;

    let height = 80;
    height += measureTextBlock(measureCtx, dateLine, fonts.kicker, contentWidth, 34);
    height += 24;
    height += measureTextBlock(measureCtx, headline, fonts.hero, contentWidth, 82);
    height += 28;
    height += measureTextBlock(measureCtx, briefing.summary, fonts.summary, contentWidth, 46);
    height += 48;

    for (const item of briefing.items) {
      height += 40;
      height += measureTextBlock(measureCtx, item.title, fonts.title, contentWidth - 84, 50);
      height += 16;
      height += measureTextBlock(measureCtx, `${item.region} · ${item.sources.join(" / ")}`, fonts.meta, contentWidth - 84, 34);
      height += 28;
      for (const [label, text] of [
        ["发生了什么", item.summary],
        ["为什么重要", item.why],
        ["后续观察", item.watch],
      ]) {
        height += 32;
        height += measureTextBlock(measureCtx, text, fonts.body, contentWidth - 84, 42);
        height += label === "后续观察" ? 8 : 18;
      }
      height += 42;
    }

    let focusHeight = 86;
    for (const focus of briefing.focus) {
      focusHeight += measureTextBlock(measureCtx, focus, fonts.body, contentWidth - 90, 42) + 18;
    }
    height += focusHeight + 52;
    height += measureTextBlock(measureCtx, "获取每日更新与历史简报", fonts.footerBold, contentWidth, 34);
    height += 16;
    height += measureTextBlock(measureCtx, websiteLine, fonts.footer, contentWidth, 34);
    height += 92;

    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = Math.ceil(height);
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = palette.bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const cardX = margin;
    const cardY = 36;
    const cardW = width - margin * 2;
    const cardH = canvas.height - 72;
    roundedRect(ctx, cardX, cardY, cardW, cardH, 22);
    ctx.fillStyle = palette.paper;
    ctx.fill();
    ctx.strokeStyle = palette.line;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    let y = cardY + 64;
    const x = cardX + pad;
    drawTextBlock(ctx, dateLine, x, y, contentWidth, fonts.kicker, 34, palette.blue);
    y += measureTextBlock(ctx, dateLine, fonts.kicker, contentWidth, 34) + 24;
    drawTextBlock(ctx, headline, x, y, contentWidth, fonts.hero, 82, palette.ink);
    y += measureTextBlock(ctx, headline, fonts.hero, contentWidth, 82) + 28;
    drawTextBlock(ctx, briefing.summary, x, y, contentWidth, fonts.summary, 46, palette.muted);
    y += measureTextBlock(ctx, briefing.summary, fonts.summary, contentWidth, 46) + 44;
    drawHairline(ctx, x, y, x + contentWidth, palette.line);
    y += 34;

    briefing.items.forEach((item, index) => {
      const number = String(index + 1).padStart(2, "0");
      roundedRect(ctx, x, y + 2, 58, 38, 19);
      ctx.fillStyle = palette.blueSoft;
      ctx.fill();
      ctx.font = fonts.number;
      ctx.fillStyle = palette.blue;
      ctx.textBaseline = "top";
      ctx.fillText(number, x + 12, y + 7);

      const tx = x + 84;
      drawTextBlock(ctx, item.title, tx, y, contentWidth - 84, fonts.title, 50, palette.ink);
      y += measureTextBlock(ctx, item.title, fonts.title, contentWidth - 84, 50) + 16;
      drawTextBlock(ctx, `${item.region} · ${item.sources.join(" / ")}`, tx, y, contentWidth - 84, fonts.meta, 34, palette.muted);
      y += measureTextBlock(ctx, `${item.region} · ${item.sources.join(" / ")}`, fonts.meta, contentWidth - 84, 34) + 28;

      for (const [label, text] of [
        ["发生了什么", item.summary],
        ["为什么重要", item.why],
        ["后续观察", item.watch],
      ]) {
        ctx.font = fonts.label;
        ctx.fillStyle = palette.blue;
        ctx.textBaseline = "top";
        ctx.fillText(label, tx, y);
        y += 32;
        drawTextBlock(ctx, text, tx, y, contentWidth - 84, fonts.body, 42, palette.ink);
        y += measureTextBlock(ctx, text, fonts.body, contentWidth - 84, 42) + (label === "后续观察" ? 8 : 18);
      }

      y += 34;
      if (index !== briefing.items.length - 1) {
        drawHairline(ctx, x, y, x + contentWidth, palette.softLine);
        y += 40;
      }
    });

    y += 16;
    const focusY = y;
    roundedRect(ctx, x, focusY, contentWidth, focusHeight, 20);
    ctx.fillStyle = palette.panel;
    ctx.fill();
    ctx.strokeStyle = palette.softLine;
    ctx.lineWidth = 1;
    ctx.stroke();
    y += 30;
    drawTextBlock(ctx, "今日重点关注", x + 34, y, contentWidth - 68, fonts.focusTitle, 44, palette.ink);
    y += 56;
    briefing.focus.forEach((focus, index) => {
      ctx.font = fonts.label;
      ctx.fillStyle = palette.blue;
      ctx.textBaseline = "top";
      ctx.fillText(`${index + 1}.`, x + 34, y + 3);
      const fy = y;
      drawTextBlock(ctx, focus, x + 76, y, contentWidth - 110, fonts.body, 42, palette.ink);
      y = fy + measureTextBlock(ctx, focus, fonts.body, contentWidth - 110, 42) + 18;
    });

    y = focusY + focusHeight + 52;
    drawTextBlock(ctx, "获取每日更新与历史简报", x, y, contentWidth, fonts.footerBold, 34, palette.ink);
    y += 42;
    drawTextBlock(ctx, websiteLine, x, y, contentWidth, fonts.footer, 34, palette.blue);
    y += 44;
    drawTextBlock(ctx, `检索日期：${briefing.date} · 覆盖范围：全球科技、财经与重大市场事件`, x, y, contentWidth, fonts.footer, 34, palette.muted);

    return canvas;
  }

  function font(size, weight) {
    return `${weight} ${size}px -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif`;
  }

  function measureTextBlock(ctx, text, fontValue, maxWidth, lineHeight) {
    return wrapText(ctx, text, fontValue, maxWidth).length * lineHeight;
  }

  function drawTextBlock(ctx, text, x, y, maxWidth, fontValue, lineHeight, color) {
    const lines = wrapText(ctx, text, fontValue, maxWidth);
    ctx.save();
    ctx.font = fontValue;
    ctx.fillStyle = color;
    ctx.textBaseline = "top";
    for (const line of lines) {
      ctx.fillText(line, x, y);
      y += lineHeight;
    }
    ctx.restore();
    return y;
  }

  function wrapText(ctx, text, fontValue, maxWidth) {
    ctx.font = fontValue;
    const value = String(text || "").replace(/\s+/g, " ").trim();
    if (!value) return [""];

    const lines = [];
    let current = "";
    for (const char of value) {
      const next = current + char;
      if (!current || ctx.measureText(next).width <= maxWidth) {
        current = next;
      } else {
        lines.push(current);
        current = char.trimStart();
      }
    }
    if (current) lines.push(current);
    return lines;
  }

  function drawHairline(ctx, x1, y, x2, color) {
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x1, y);
    ctx.lineTo(x2, y);
    ctx.stroke();
    ctx.restore();
  }

  function roundedRect(ctx, x, y, width, height, radius) {
    const r = Math.min(radius, width / 2, height / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + width - r, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + r);
    ctx.lineTo(x + width, y + height - r);
    ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
    ctx.lineTo(x + r, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  renderCards(Boolean(openDate));
})();
