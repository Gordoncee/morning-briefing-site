#!/usr/bin/env python3
"""Build the independent daily-news Pages site from Markdown; standard library only.

Each archive/briefings/YYYY/MM/YYYY-MM-DD.md contains its complete structured
briefing in a versioned fenced ``json`` envelope, read by news_archive.
No model, feed, application server, database, or network is used at build time.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
from html import escape
import json
from pathlib import Path
import shutil
from string import Template
from urllib.parse import urljoin, urlsplit

if __package__:
    from .news_archive import load_briefings
else:
    from news_archive import load_briefings

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_URL = "https://gordoncee.github.io/morning-briefing-site/"
# Use the reachable case entry while the domain is awaiting ICP clearance.
# Both addresses serve the same release directory on the ECS.
DEFAULT_CASE_SITE = "http://47.117.77.217"
BRAND = "AI法智前沿"
NAVIGATION_VERSION = "20261023"
COMPATIBILITY_FILES = (
    "admin.html", "admin.css", "admin.js", "styles.css",
    "analytics-config.js", "analytics.js",
)


def h(value: object) -> str:
    return escape(str(value), quote=True)


def http_url(value: object) -> str:
    """RSS and model output are content, never executable URLs."""
    text = str(value or "").strip()
    try:
        parsed = urlsplit(text)
    except ValueError:
        return ""
    return text if parsed.scheme in {"https", "http"} and parsed.netloc else ""


def strings(value: object, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be an array of strings")
    return value


def validate_briefing(payload: dict) -> dict:
    row = dict(payload)
    label = f"Briefing {row.get('date', 'unknown')}"
    if not isinstance(row, dict):
        raise ValueError(f"{label}: briefing metadata must be an object")
    stamp = str(row.get("date", ""))
    try:
        parsed = date.fromisoformat(stamp)
    except ValueError as error:
        raise ValueError(f"{label}: invalid briefing date {stamp!r}") from error
    if parsed.isoformat() != stamp:
        raise ValueError(f"{label}: date must use YYYY-MM-DD")
    for field in ("summary", "scope", "displayDate"):
        if field in row and not isinstance(row[field], str):
            raise ValueError(f"{label}: {field} must be a string")
    row.setdefault("displayDate", f"{parsed.year}年{parsed.month}月{parsed.day}日")
    row.setdefault("scope", "全球新闻｜科技与财经优先")
    row.setdefault("summary", "")
    row["focus"] = strings(row.get("focus"), f"{label}: focus")
    row["sourceLinks"] = strings(row.get("sourceLinks"), f"{label}: sourceLinks")
    items = row.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError(f"{label}: items must be a non-empty array")
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"{label}: each item must be an object")
        for field in ("title", "summary"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"{label}: each item needs non-empty {field}")
        for field in ("region", "why", "watch"):
            if not isinstance(item.get(field, ""), str):
                raise ValueError(f"{label}: item {field} must be a string")
        item["sources"] = strings(item.get("sources"), f"{label}: item sources")
    return row


def read_archive(archive_dir: Path) -> list[dict]:
    rows = [validate_briefing(row) for row in load_briefings(archive_dir)]
    dates = [row["date"] for row in rows]
    if len(dates) != len(set(dates)):
        raise ValueError("Duplicate briefing dates in Markdown archive")
    if not rows:
        raise ValueError(f"No briefing Markdown files found in {archive_dir}")
    return sorted(rows, key=lambda row: row["date"], reverse=True)


def template(directory: Path, name: str, **values: object) -> str:
    return Template((directory / name).read_text(encoding="utf-8")).substitute(values)


def focus_tags(values: list[str], limit: int | None = None, truncate: int = 0) -> str:
    def shorten(value: str) -> str:
        return value[:truncate - 1] + "…" if truncate and len(value) > truncate else value
    return "".join(f'<span title="{h(value)}">{h(shorten(value))}</span>'
                   for value in (values if limit is None else values[:limit]))


def news_home_url(home: str) -> str:
    return f"{home}?v={NAVIGATION_VERSION}"


def detail_url(home: str, row: dict) -> str:
    return f"{home}{row['date']}/"


def render_list(rows: list[dict], template_dir: Path, home: str, backdrop: str) -> str:
    latest = rows[0] if rows else None
    month_counts = Counter(row["date"][:7] for row in rows)
    buttons = "".join(
        f'<button type="button" class="news-month-button" data-news-month="{month}" '
        f'aria-pressed="false"><span>{month[:4]}年{int(month[5:])}月</span><span>{count}</span></button>'
        for month, count in sorted(month_counts.items(), reverse=True)
    )
    cards = []
    for row in rows:
        search = " ".join([row["date"], row["displayDate"], row["summary"],
                           *(item["title"] for item in row["items"]), *row["focus"]])
        cards.append(
            f'<a class="news-archive-card" href="{h(detail_url(home, row))}" data-news-entry data-news-date="{row["date"]}" '
            f'data-month="{row["date"][:7]}" data-search="{h(search)}">'
            f'<div class="news-card-date"><time datetime="{row["date"]}">{row["date"]}</time>'
            '<span aria-hidden="true">↗</span></div>'
            f'<h3>{h(row["displayDate"])}简报</h3><p class="news-card-summary">{h(row["summary"])}</p>'
            '<div class="news-card-bottom"><div class="news-card-focus">'
            f'{focus_tags(row["focus"], 2, 22)}</div><span class="news-card-count">'
            f'{len(row["items"])} 条要闻</span></div></a>'
        )
    latest_section = ""
    if latest:
        url = h(detail_url(home, latest))
        topics = "".join(
            f'<li><a href="{url}#news-item-{index}"><span class="news-topic-number">{index:02d}</span>'
            f'<span>{h(item["title"])}</span><span class="news-topic-arrow" aria-hidden="true">↗</span></a></li>'
            for index, item in enumerate(latest["items"], 1)
        )
        latest_section = (
            '<section class="news-latest" aria-labelledby="news-latest-heading">'
            '<div class="news-latest-copy"><span class="mini-label"><span class="status-dot"></span> 最新一期</span>'
            f'<h2 id="news-latest-heading"><a href="{url}">{h(latest["displayDate"])}</a></h2>'
            f'<p class="news-latest-summary">{h(latest["summary"])}</p>'
            f'<div class="news-focus-tags" aria-label="本期关注">{focus_tags(latest["focus"], truncate=32)}</div>'
            f'<a class="news-read-link" href="{url}">阅读本期简报 <span aria-hidden="true">↗</span></a></div>'
            f'<div class="news-latest-topics"><span class="mini-label">本期要闻 · {len(latest["items"])} 条</span>'
            f'<ol>{topics}</ol></div></section>'
        )
    return template(
        template_dir, "list.html", backdrop=backdrop, briefing_count=len(rows),
        latest_date=f'<span>最近更新 {latest["date"]}</span>' if latest else "",
        latest_section=latest_section, month_buttons=buttons, archive_cards="".join(cards),
        archive_since=f'<p class="news-archive-since">自 {h(rows[-1]["displayDate"])} 起收录</p>' if rows else "",
        empty_hidden="hidden" if rows else "",
    )


def render_detail(row: dict, older: dict | None, newer: dict | None, template_dir: Path,
                  home: str, backdrop: str, image_url: str = "") -> str:
    items, reading_index = [], []
    for index, item in enumerate(row["items"], 1):
        metadata = "".join(f"<span>{h(value)}</span>" for value in [
            item.get("region", ""), " / ".join(item["sources"])] if value)
        paragraphs = f'<div><h3>发生了什么</h3><p>{h(item["summary"])}</p></div>'
        if item.get("why"):
            paragraphs += f'<div><h3>为什么重要</h3><p>{h(item["why"])}</p></div>'
        if item.get("watch"):
            paragraphs += f'<div class="news-item-watch"><h3>后续观察</h3><p>{h(item["watch"])}</p></div>'
        items.append(
            f'<section class="news-item" id="news-item-{index}" aria-labelledby="news-item-title-{index}">'
            f'<div class="news-item-heading"><span class="news-item-number">{index:02d}</span><div>'
            f'<p class="news-item-meta">{metadata}</p><h2 id="news-item-title-{index}">{h(item["title"])}</h2>'
            f'</div></div><div class="news-item-body">{paragraphs}</div></section>'
        )
        reading_index.append(f'<li><a href="#news-item-{index}"><span>{index:02d}</span>{h(item["title"])}</a></li>')
    nav = (
        f'<a href="{h(detail_url(home, older))}"><span>← 较早一期</span><strong>{h(older["displayDate"])}</strong></a>'
        if older else "<div></div>"
    )
    nav += (
        f'<a href="{h(detail_url(home, newer))}"><span>较新一期 →</span><strong>{h(newer["displayDate"])}</strong></a>'
        if newer else f'<a href="{h(news_home_url(home))}#news-archive"><span>日期归档 →</span><strong>查看全部资讯</strong></a>'
    )
    source_items = "".join(
        f'<li><a href="{h(url)}" target="_blank" rel="noopener noreferrer" data-news-source>'
        f'<span class="news-source-name">{h(url)}</span><span aria-hidden="true">↗</span></a></li>'
        for value in row["sourceLinks"] if (url := http_url(value))
    )
    return template(
        template_dir, "detail.html", backdrop=backdrop, news_home=h(news_home_url(home)),
        display_date=h(row["displayDate"]), scope=h(row["scope"]), date=row["date"],
        item_count=len(row["items"]), summary=h(row["summary"]), items="".join(items),
        reading_index="".join(reading_index), issue_nav=nav,
        focus_card=(
            '<section class="news-side-card"><h2>重点关注</h2><div class="news-focus-tags">'
            f'{focus_tags(row["focus"])}</div></section>' if row["focus"] else ""
        ),
        sources_card=(
            '<section class="news-side-card news-sources" id="news-sources"><h2>本期来源</h2>'
            f'<p>查看本期简报所列原文。</p><ol>{source_items}</ol></section>' if source_items else ""
        ),
        image_link=(f'<a href="{h(image_url)}" target="_blank" rel="noopener noreferrer">'
                    '查看分享图 <span aria-hidden="true">↗</span></a>' if image_url else ""),
    )


def make_site_url(value: str) -> tuple[str, str]:
    url = http_url(value)
    if not url:
        raise ValueError("--site-url must be an absolute HTTP(S) URL")
    parsed = urlsplit(url)
    if parsed.query or parsed.fragment:
        raise ValueError("--site-url must not contain a query or fragment")
    site_url = url.rstrip("/") + "/"
    home = urlsplit(site_url).path or "/"
    return site_url, home


def build_site(archive_dir: Path, output: Path, design_dir: Path, site_url: str,
               case_site: str, legacy_images: Path | None = None,
               compatibility_root: Path | None = None) -> dict:
    rows = read_archive(archive_dir)
    site_url, home = make_site_url(site_url)
    case_site = http_url(case_site).rstrip("/")
    if not case_site or urlsplit(case_site).query or urlsplit(case_site).fragment:
        raise ValueError("--case-site must be an absolute HTTP(S) URL without query or fragment")
    output = output.resolve()
    archive_dir = archive_dir.resolve()
    design_dir = design_dir.resolve()
    # The builder can only write into a dedicated export directory, never its inputs.
    for source in (archive_dir, design_dir, REPO_ROOT / "scripts"):
        if output == source or output in source.parents or source in output.parents:
            raise ValueError(f"Output overlaps source directory: {source}")
    output.mkdir(parents=True, exist_ok=True)
    templates = design_dir / "templates"
    assets = design_dir / "assets"
    version = hashlib.sha256()
    for path in sorted(assets.rglob("*")):
        if path.is_file():
            version.update(path.relative_to(assets).as_posix().encode("utf-8"))
            version.update(path.read_bytes())
    asset_version = version.hexdigest()[:12]
    shutil.copytree(assets, output / "static" / "atlas", dirs_exist_ok=True)
    # Preserve already-public legacy paths without putting their entry points in
    # the new navigation or changing the analytics/admin authentication logic.
    compatibility_root = compatibility_root or REPO_ROOT
    copied_compatibility = []
    for name in COMPATIBILITY_FILES:
        source = compatibility_root / name
        if source.is_file():
            shutil.copyfile(source, output / name)
            copied_compatibility.append(name)
    # This compatibility export is derived from Markdown; never parse/evaluate
    # the old JS. The new homepage only uses its rendered archive-card metadata.
    compatibility_data = output / "data" / "briefings.js"
    compatibility_data.parent.mkdir(parents=True, exist_ok=True)
    compatibility_data.write_text(
        "window.MORNING_BRIEFINGS=" + json.dumps(
            rows, ensure_ascii=False, separators=(",", ":"), allow_nan=False,
        ) + ";\n", encoding="utf-8",
    )
    asset_base = f"{home}static/atlas/"
    backdrop = (
        '<div class="hero-underlay" aria-hidden="true"></div>'
        f'<img class="hero-artwork" src="{h(asset_base)}brand/hero-muted-20261014.webp" '
        'alt="" aria-hidden="true" width="1942" height="809" fetchpriority="high" decoding="async">'
        '<canvas class="hero-liquid" aria-hidden="true"></canvas>'
    )
    brand_markup = (
        f'<img class="brand-logo" src="{h(asset_base)}brand/ai-law-frontier.jpg" alt="" width="42" height="42">'
        f'<span class="brand-name">{BRAND}<span class="brand-caption">AI案例研究库</span></span>'
    )

    def page(content: str, title: str, description: str, stamp: str = "") -> str:
        return template(
            templates, "base.html", brand=BRAND, team_name="AI法智前沿研究团队",
            title=h(title), description=h(description), content=content,
            case_site=h(case_site), news_home=h(news_home_url(home)), asset_base=h(asset_base),
            brand_markup=brand_markup, asset_version=asset_version,
            community_feedback=template(templates, "community_feedback.html", asset_base=h(asset_base)),
            canonical=h(urljoin(site_url, f"{stamp}/" if stamp else "")),
            og_type="article" if stamp else "website",
        )

    (output / "index.html").write_text(page(
        render_list(rows, templates, home, backdrop), f"每日资讯 · {BRAND}",
        "关注全球科技、财经与 AI 产业动向，按日期查阅每日简报及新闻来源。",
    ), encoding="utf-8")
    copied_images = 0
    for index, row in enumerate(rows):
        older = rows[index + 1] if index + 1 < len(rows) else None
        newer = rows[index - 1] if index > 0 else None
        image_url = ""
        if legacy_images and row.get("image"):
            # Copy only a local legacy image that is explicitly referenced by this issue.
            image_name = Path(str(row["image"])).name
            image = legacy_images / image_name
            if image_name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")) and image.is_file():
                image_output = output / "assets" / image_name
                image_output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(image, image_output)
                copied_images += 1
                image_url = urljoin(site_url, f"assets/{image_name}")
        directory = output / row["date"]
        directory.mkdir(exist_ok=True)
        directory.joinpath("index.html").write_text(page(
            render_detail(row, older, newer, templates, home, backdrop, image_url),
            f"{row['displayDate']}每日资讯 · {BRAND}", row["summary"], row["date"],
        ), encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    return {"briefings": len(rows), "latest": rows[0]["date"], "pages": len(rows) + 1,
            "compatibility_files": copied_compatibility + ["data/briefings.js"],
            "legacy_images": copied_images, "output": str(output), "site_url": site_url}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", type=Path, default=REPO_ROOT / "archive" / "briefings")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "dist")
    parser.add_argument("--design-dir", type=Path, default=REPO_ROOT / "site")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL)
    parser.add_argument("--case-site", default=DEFAULT_CASE_SITE)
    parser.add_argument("--legacy-images", type=Path, help="Optionally retain existing share images from this directory")
    args = parser.parse_args()
    report = build_site(args.archive_dir, args.output, args.design_dir, args.site_url,
                        args.case_site, args.legacy_images)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
