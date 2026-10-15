(() => {
  const archive = document.getElementById('news-archive');
  if (archive) {
    // Links shared by the original briefing site used #YYYY-MM-DD.
    // Redirect only dates present in this archive to their permanent issue page.
    const redirectLegacyIssue = () => {
      const stamp = window.location.hash.slice(1);
      if (!/^\d{4}-\d{2}-\d{2}$/.test(stamp)) return false;
      const entry = archive.querySelector(`[data-news-date="${stamp}"]`);
      if (!entry) return false;
      window.location.replace(entry.href);
      return true;
    };
    if (redirectLegacyIssue()) return;
    window.addEventListener('hashchange', redirectLegacyIssue);
    const entries = Array.from(archive.querySelectorAll('[data-news-entry]'));
    const monthButtons = Array.from(archive.querySelectorAll('[data-news-month]'));
    const search = document.getElementById('news-search');
    const reset = document.getElementById('news-filter-reset');
    const count = document.getElementById('news-result-count');
    const monthLabel = document.getElementById('news-month-label');
    const empty = document.getElementById('news-empty');
    const more = document.getElementById('news-load-more');
    const moreWrap = document.getElementById('news-load-more-wrap');
    const visibleCount = document.getElementById('news-visible-count');
    const pageSize = 12;
    let selectedMonth = '';
    let visibleLimit = pageSize;
    const normalize = value => String(value || '').normalize('NFKC').toLocaleLowerCase().trim();
    const index = entries.map(element => ({ element, month: element.dataset.month, text: normalize(element.dataset.search) }));

    function render() {
      const terms = normalize(search.value).split(/\s+/).filter(Boolean);
      let matches = 0;
      index.forEach(entry => {
        const match = (!selectedMonth || entry.month === selectedMonth) && terms.every(term => entry.text.includes(term));
        entry.element.hidden = !match || matches >= visibleLimit;
        if (match) matches += 1;
      });
      count.textContent = String(matches);
      empty.hidden = matches > 0;
      reset.hidden = !selectedMonth && terms.length === 0;
      moreWrap.hidden = matches <= visibleLimit;
      visibleCount.textContent = `已显示 ${Math.min(matches, visibleLimit)} / ${matches} 期`;
      monthButtons.forEach(button => {
        const active = button.dataset.newsMonth === selectedMonth;
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', String(active));
        if (active) monthLabel.textContent = button.querySelector('span').textContent;
      });
    }
    search.addEventListener('input', () => { visibleLimit = pageSize; render(); });
    monthButtons.forEach(button => button.addEventListener('click', () => {
      selectedMonth = button.dataset.newsMonth;
      visibleLimit = pageSize;
      render();
    }));
    reset.addEventListener('click', () => { selectedMonth = ''; search.value = ''; visibleLimit = pageSize; render(); });
    more.addEventListener('click', () => {
      const previouslyVisible = new Set(entries.filter(entry => !entry.hidden));
      visibleLimit += pageSize;
      render();
      const firstNewEntry = entries.find(entry => !entry.hidden && !previouslyVisible.has(entry));
      if (firstNewEntry) firstNewEntry.focus({ preventScroll: true });
    });
    render();
  }

  // Keep the original source URLs while making the reading list easy to scan.
  document.querySelectorAll('[data-news-source]').forEach(link => {
    try {
      const url = new URL(link.href);
      const name = link.querySelector('.news-source-name');
      let domain = url.hostname.replace(/^www\./, '');
      if (domain === 'news.google.com') domain = 'Google News';
      name.textContent = domain;
      link.title = url.href;
      link.setAttribute('aria-label', `查看来源：${domain}（在新标签页打开）`);
    } catch (error) { /* The original URL stays visible if parsing fails. */ }
  });

  const copyButton = document.querySelector('[data-news-copy]');
  if (copyButton) {
    const status = document.querySelector('[data-news-copy-status]');
    copyButton.addEventListener('click', async () => {
      const shareUrl = new URL(window.location.href);
      shareUrl.hash = '';
      try {
        await navigator.clipboard.writeText(shareUrl.href);
        status.textContent = '链接已复制';
      } catch (error) {
        status.textContent = '选中并复制下方链接：';
        const input = document.createElement('input');
        input.type = 'text';
        input.value = shareUrl.href;
        input.readOnly = true;
        input.setAttribute('aria-label', '本期资讯链接');
        status.appendChild(input);
        input.focus();
        input.select();
      }
    });
  }
})();
