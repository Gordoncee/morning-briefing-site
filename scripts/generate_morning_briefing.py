#!/usr/bin/env python3
"""Generate and publish one morning briefing entry.

The script is intentionally dependency-light. It uses RSS feeds as the news
candidate pool, an OpenAI-compatible chat/completions endpoint for synthesis,
and Pillow for the share image.
"""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import html
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "briefings.js"
ASSETS_DIR = ROOT / "assets"
INDEX_FILE = ROOT / "index.html"

DEFAULT_FEEDS = [
    "https://apnews.com/hub/business?output=rss",
    "https://apnews.com/hub/technology?output=rss",
    "https://www.axios.com/feed",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.marketwatch.com/marketwatch/topstories",
    "https://www.investors.com/feed/",
    "https://www.wsj.com/xml/rss/3_7014.xml",
    "https://www.barrons.com/xml/rss/3_7031.xml",
]

GOOGLE_NEWS_QUERIES = [
    "AI technology finance markets",
    "artificial intelligence data center chips business",
    "technology stocks finance economy",
    "semiconductor AI earnings market",
    "global business technology AI",
]


class BriefingError(RuntimeError):
    pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=os.environ.get("BRIEFING_DATE", ""))
    parser.add_argument("--max-candidates", type=int, default=int(os.environ.get("MAX_NEWS_CANDIDATES", "30")))
    args = parser.parse_args()

    today = parse_date(args.date)
    previous = load_existing_briefings(DATA_FILE)
    candidates = collect_candidates(args.max_candidates)
    if len(candidates) < 12:
        raise BriefingError(f"Only collected {len(candidates)} news candidates; refusing to publish weak briefing.")

    briefing = synthesize_briefing(today, candidates, previous)
    validate_briefing(briefing, today)
    upsert_briefing(DATA_FILE, briefing)
    update_cache_bust(INDEX_FILE, today)
    render_share_image(briefing, ASSETS_DIR / f"morning-briefing-{today.isoformat()}.png")
    print(json.dumps({"date": briefing["date"], "items": len(briefing["items"]), "image": briefing["image"]}, ensure_ascii=False))
    return 0


def parse_date(value: str) -> dt.date:
    if value:
        return dt.date.fromisoformat(value)
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()


def provider_config() -> dict[str, str]:
    provider = os.environ.get("MODEL_PROVIDER", "kimi").strip().lower()
    model_name = os.environ.get("MODEL_NAME", "").strip()
    if provider == "kimi":
        return {
            "provider": provider,
            "base_url": (os.environ.get("LLM_BASE_URL") or "https://api.moonshot.cn/v1").rstrip("/"),
            "api_key": os.environ.get("MOONSHOT_API_KEY", ""),
            "model": model_name or os.environ.get("KIMI_MODEL", "kimi-k2.6"),
        }
    if provider == "openai":
        return {
            "provider": provider,
            "base_url": (os.environ.get("LLM_BASE_URL") or "https://api.openai.com/v1").rstrip("/"),
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "model": model_name or os.environ.get("OPENAI_MODEL", "gpt-5.1"),
        }
    if provider == "qwen":
        return {
            "provider": provider,
            "base_url": (os.environ.get("LLM_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1").rstrip("/"),
            "api_key": os.environ.get("DASHSCOPE_API_KEY", ""),
            "model": model_name or os.environ.get("QWEN_MODEL", "qwen-plus"),
        }
    if provider == "custom":
        return {
            "provider": provider,
            "base_url": os.environ.get("LLM_BASE_URL", "").rstrip("/"),
            "api_key": os.environ.get("LLM_API_KEY", ""),
            "model": model_name,
        }
    raise BriefingError(f"Unsupported MODEL_PROVIDER: {provider}")


def collect_candidates(limit: int) -> list[dict[str, str]]:
    feeds = list(DEFAULT_FEEDS)
    for query in GOOGLE_NEWS_QUERIES:
        encoded = urllib.parse.quote(query)
        feeds.append(f"https://news.google.com/rss/search?q={encoded}%20when:2d&hl=en-US&gl=US&ceid=US:en")

    seen: set[str] = set()
    candidates: list[dict[str, str]] = []
    per_feed_limit = max(5, min(10, limit // 4))
    for feed in feeds:
        added_from_feed = 0
        for item in fetch_feed(feed):
            key = normalized_url(item["url"]) or item["title"].casefold()
            if not key or key in seen:
                continue
            seen.add(key)
            candidates.append(item)
            added_from_feed += 1
            if len(candidates) >= limit:
                return candidates
            if added_from_feed >= per_feed_limit:
                break
    return candidates


def fetch_feed(url: str) -> list[dict[str, str]]:
    try:
        raw = http_get(url, timeout=20)
    except Exception as exc:  # noqa: BLE001
        print(f"warning: failed to fetch feed {url}: {exc}", file=sys.stderr)
        return []
    try:
        root = ET.fromstring(clean_xml(raw))
    except ET.ParseError as exc:
        print(f"warning: failed to parse feed {url}: {exc}", file=sys.stderr)
        return []

    items: list[dict[str, str]] = []
    channel_items = root.findall(".//item")
    if channel_items:
        for node in channel_items:
            title = text_of(node, "title")
            link = text_of(node, "link")
            summary = clean_html(text_of(node, "description"))
            source = text_of(node, "source") or hostname(link)
            published = text_of(node, "pubDate")
            items.append(make_candidate(title, link, summary, source, published))
        return [item for item in items if item["title"] and item["url"]]

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for node in root.findall(".//atom:entry", ns):
        title = node.findtext("atom:title", default="", namespaces=ns)
        link_node = node.find("atom:link", ns)
        link = link_node.attrib.get("href", "") if link_node is not None else ""
        summary = clean_html(node.findtext("atom:summary", default="", namespaces=ns))
        published = node.findtext("atom:updated", default="", namespaces=ns)
        items.append(make_candidate(title, link, summary, hostname(link), published))
    return [item for item in items if item["title"] and item["url"]]


def make_candidate(title: str, url: str, summary: str, source: str, published: str) -> dict[str, str]:
    return {
        "title": clean_space(title),
        "url": clean_space(url),
        "source": clean_space(source or hostname(url)),
        "summary": truncate(clean_space(summary), 220),
        "published": normalize_date(published),
    }


def http_get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "morning-briefing-bot/1.0 (+https://gordoncee.github.io/morning-briefing-site/)",
            "Accept": "application/rss+xml, application/xml, text/xml, text/html;q=0.8, */*;q=0.5",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:  # noqa: S310
        return response.read()


def clean_xml(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="replace")
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)


def text_of(node: ET.Element, tag: str) -> str:
    child = node.find(tag)
    if child is None or child.text is None:
        return ""
    return child.text


def clean_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return clean_space(html.unescape(value))


def clean_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def truncate(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def hostname(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.replace("www.", "")
    except Exception:  # noqa: BLE001
        return ""


def normalized_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip("/"), "", "", ""))


def normalize_date(value: str) -> str:
    if not value:
        return ""
    try:
        return email.utils.parsedate_to_datetime(value).isoformat()
    except Exception:  # noqa: BLE001
        return clean_space(value)


def load_existing_briefings(path: Path) -> list[dict[str, Any]]:
    content = path.read_text(encoding="utf-8")
    dates = re.findall(r'date:\s*"(\d{4}-\d{2}-\d{2})"', content)
    titles = re.findall(r'title:\s*"([^"]+)"', content)
    links = re.findall(r'"https?://[^"]+"', content)
    return [{"dates": dates[:14], "titles": titles[:60], "links": [link.strip('"') for link in links[-120:]]}]


def synthesize_briefing(today: dt.date, candidates: list[dict[str, str]], previous: list[dict[str, Any]]) -> dict[str, Any]:
    cfg = provider_config()
    if not cfg["api_key"]:
        raise BriefingError(f"Missing API key for provider {cfg['provider']}.")
    if not cfg["base_url"] or not cfg["model"]:
        raise BriefingError("Missing model base_url or model name.")

    system = (
        "你是严谨的中文科技财经晨间简报编辑。你的任务是从候选新闻中选出最值得关注、"
        "可交叉核验、与近期简报不重复的全球科技财经新闻，生成结构化 JSON。"
    )
    prompt = {
        "date": today.isoformat(),
        "displayDate": f"{today.year}年{today.month}月{today.day}日",
        "requirements": [
            "优先科技、财经、资本市场、AI、芯片、云基础设施、平台监管和重大宏观变量。",
            "选5条；只有在候选新闻明显不足时才少于5条，并在summary解释原因。",
            "每条新闻必须基于候选列表中的来源；sourceLinks只能使用候选列表中的真实URL。",
            "避免重复近期标题和主线。不要编造来源、日期、人物、金额。",
            "快速决策，不要输出推理过程，只输出最终JSON。",
            "输出必须是纯JSON，不要Markdown。字段必须为 date, displayDate, scope, image, summary, focus, items, sourceLinks。",
            "items每条字段必须为 title, region, sources, summary, why, watch。",
        ],
        "recent": previous[0] if previous else {},
        "candidates": candidates,
    }
    data = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ],
        "temperature": model_temperature(cfg["provider"]),
    }
    raw = post_json(f"{cfg['base_url']}/chat/completions", cfg["api_key"], data)
    try:
        content = raw["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise BriefingError(f"Unexpected LLM response shape: {raw}") from exc
    briefing = parse_json_object(content)
    briefing["date"] = today.isoformat()
    briefing["displayDate"] = f"{today.year}年{today.month}月{today.day}日"
    briefing["scope"] = "全球新闻｜科技与财经优先"
    briefing["image"] = f"assets/morning-briefing-{today.isoformat()}.png"
    return briefing


def post_json(url: str, api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as response:  # noqa: S310
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise BriefingError(f"LLM API HTTP {exc.code}: {detail[:1200]}") from exc


def model_temperature(provider: str) -> float:
    if os.environ.get("LLM_TEMPERATURE"):
        return float(os.environ["LLM_TEMPERATURE"])
    return 1.0 if provider == "kimi" else 0.2


def parse_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise
        return json.loads(text[start : end + 1])


def validate_briefing(briefing: dict[str, Any], today: dt.date) -> None:
    required = ["date", "displayDate", "scope", "image", "summary", "focus", "items", "sourceLinks"]
    for key in required:
        if key not in briefing:
            raise BriefingError(f"Missing briefing field: {key}")
    if briefing["date"] != today.isoformat():
        raise BriefingError(f"Unexpected date: {briefing['date']}")
    if not isinstance(briefing["items"], list) or len(briefing["items"]) < 3:
        raise BriefingError("Briefing must contain at least 3 items.")
    if len(briefing["items"]) > 5:
        briefing["items"] = briefing["items"][:5]
    for item in briefing["items"]:
        for key in ["title", "region", "sources", "summary", "why", "watch"]:
            if key not in item or not item[key]:
                raise BriefingError(f"Invalid item missing {key}: {item}")
        if isinstance(item["sources"], str):
            item["sources"] = [item["sources"]]
    if isinstance(briefing["focus"], str):
        briefing["focus"] = [briefing["focus"]]
    if not isinstance(briefing["focus"], list):
        briefing["focus"] = []
    briefing["focus"] = [str(item).strip() for item in briefing["focus"] if str(item).strip()]
    for item in briefing["items"]:
        if len(briefing["focus"]) >= 3:
            break
        briefing["focus"].append(item["why"])
    if len(briefing["focus"]) < 3:
        briefing["focus"].append(briefing["summary"])
    briefing["focus"] = briefing["focus"][:3]
    if not isinstance(briefing["sourceLinks"], list) or len(briefing["sourceLinks"]) < 3:
        raise BriefingError("Briefing must contain sourceLinks.")


def upsert_briefing(path: Path, briefing: dict[str, Any]) -> None:
    content = path.read_text(encoding="utf-8")
    date = briefing["date"]
    content = remove_existing_entry(content, date)
    literal = json.dumps(briefing, ensure_ascii=False, indent=2)
    indented = "\n".join(f"  {line}" for line in literal.splitlines())
    marker = "window.MORNING_BRIEFINGS = [\n"
    if marker not in content:
        raise BriefingError("Could not find MORNING_BRIEFINGS array marker.")
    updated = content.replace(marker, f"{marker}{indented},\n", 1)
    path.write_text(updated, encoding="utf-8")


def remove_existing_entry(content: str, date: str) -> str:
    marker = f'"date": "{date}"'
    index = content.find(marker)
    if index == -1:
        marker = f'date: "{date}"'
        index = content.find(marker)
    if index == -1:
        return content

    start = content.rfind("{", 0, index)
    if start == -1:
        raise BriefingError(f"Could not locate start of existing {date} entry.")
    depth = 0
    in_string = False
    escaped = False
    for pos in range(start, len(content)):
        ch = content[pos]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = pos + 1
                if content[end : end + 2] == ",\n":
                    end += 2
                elif content[end : end + 1] == ",":
                    end += 1
                return content[:start] + content[end:]
    raise BriefingError(f"Could not locate end of existing {date} entry.")


def update_cache_bust(path: Path, today: dt.date) -> None:
    value = today.strftime("%Y%m%d")
    image_url = f"https://gordoncee.github.io/morning-briefing-site/assets/morning-briefing-{today.isoformat()}.png"
    content = path.read_text(encoding="utf-8")
    content = re.sub(r'data/briefings\.js\?v=[^"]+', f"data/briefings.js?v={value}", content)
    content = re.sub(r'app\.js\?v=[^"]+', f"app.js?v={value}", content)
    content = re.sub(r'property="og:image"\s+content="[^"]+"', f'property="og:image" content="{image_url}"', content)
    content = re.sub(r'name="twitter:image"\s+content="[^"]+"', f'name="twitter:image" content="{image_url}"', content)
    path.write_text(content, encoding="utf-8")


def render_share_image(briefing: dict[str, Any], out: Path) -> None:
    width = 1242
    margin = 72
    card_width = width - margin * 2
    content_width = card_width - 64 * 2
    colors = {
        "bg": "#f7f4ec",
        "paper": "#fffdf8",
        "ink": "#1f2529",
        "muted": "#687078",
        "teal": "#16484e",
        "teal2": "#0f7480",
        "red": "#b8503e",
        "gold": "#dcae55",
        "line": "#d8d2c5",
        "soft": "#e8e1d2",
    }

    regular = first_existing_font(
        [
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
    )
    bold = first_existing_font(
        [
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        ]
    )

    def font(size: int, is_bold: bool = False) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(bold if is_bold else regular), size)

    body = font(28)
    body_bold = font(28, True)
    sub = font(22)
    sub_bold = font(22, True)
    title_font = font(42, True)
    hero_font = font(68, True)
    num_font = font(28, True)

    def wrap(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        lines: list[str] = []
        current = ""
        for ch in str(text):
            test = current + ch
            if draw.textbbox((0, 0), test, font=font_obj)[2] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = ch
        if current:
            lines.append(current)
        return lines or [""]

    def paragraph(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont, max_width: int, gap: int = 10) -> tuple[list[str], int, int]:
        lines = wrap(draw, text, font_obj, max_width)
        bbox = draw.textbbox((0, 0), "测A", font=font_obj)
        line_height = bbox[3] - bbox[1] + gap
        return lines, line_height, len(lines) * line_height

    measure = Image.new("RGB", (width, 100), colors["bg"])
    dm = ImageDraw.Draw(measure)
    height = 292 + paragraph(dm, briefing["summary"], body, content_width)[2] + 34
    for item in briefing["items"]:
        height += 34 + paragraph(dm, item["title"], title_font, content_width - 96)[2]
        for text, font_obj in [
            (f"地区/主体：{item['region']}", sub),
            (f"来源：{'｜'.join(item['sources'])}", sub),
            (f"摘要：{item['summary']}", body),
            (f"为什么值得关注：{item['why']}", body),
            (f"后续观察：{item['watch']}", body),
        ]:
            height += paragraph(dm, text, font_obj, content_width - 96)[2] + 10
        height += 54
    focus_inner = 80
    for focus in briefing["focus"]:
        focus_inner += paragraph(dm, focus, body, content_width - 110)[2] + 14
    focus_height = focus_inner + 34
    height += focus_height + 152

    image = Image.new("RGB", (width, height), colors["bg"])
    draw = ImageDraw.Draw(image)
    card_x0, card_y0, card_x1, card_y1 = margin, 36, width - margin, height - 36
    draw.rounded_rectangle((card_x0, card_y0, card_x1, card_y1), radius=34, fill=colors["paper"], outline=colors["line"], width=2)
    x = card_x0 + 64
    y = card_y0 + 52
    draw.rounded_rectangle((x, y, x + 220, y + 46), radius=10, fill=colors["teal"])
    draw.text((x + 18, y + 9), "MORNING BRIEFING", font=sub_bold, fill=colors["paper"])
    y += 74
    draw.text((x, y), briefing["displayDate"], font=hero_font, fill=colors["ink"])
    y += 86
    draw.text((x, y), briefing["scope"], font=body_bold, fill=colors["teal2"])
    y += 52
    lines, lh, _ = paragraph(draw, briefing["summary"], body, content_width)
    for line in lines:
        draw.text((x, y), line, font=body, fill=colors["muted"])
        y += lh
    y += 28
    draw.line((x, y, card_x1 - 64, y), fill=colors["soft"], width=2)
    y += 34

    for index, item in enumerate(briefing["items"], start=1):
        draw.rounded_rectangle((x, y, card_x1 - 64, y + 10), radius=5, fill=colors["bg"])
        y += 24
        draw.rounded_rectangle((x, y, x + 56, y + 56), radius=14, fill=colors["red"])
        draw.text((x + 14, y + 11), f"{index:02d}", font=num_font, fill=colors["paper"])
        tx = x + 82
        yy = y - 2
        lines, lh, _ = paragraph(draw, item["title"], title_font, content_width - 96)
        for line in lines:
            draw.text((tx, yy), line, font=title_font, fill=colors["ink"])
            yy += lh
        y = yy + 8
        for text, font_obj, color in [
            (f"地区/主体：{item['region']}", sub, colors["muted"]),
            (f"来源：{'｜'.join(item['sources'])}", sub, colors["muted"]),
            (f"摘要：{item['summary']}", body, colors["ink"]),
            (f"为什么值得关注：{item['why']}", body, colors["ink"]),
            (f"后续观察：{item['watch']}", body, colors["ink"]),
        ]:
            lines, lh, _ = paragraph(draw, text, font_obj, content_width - 96)
            for line in lines:
                draw.text((tx, y), line, font=font_obj, fill=color)
                y += lh
            y += 10
        y += 18
        if index != len(briefing["items"]):
            draw.line((x, y, card_x1 - 64, y), fill=colors["soft"], width=2)
            y += 28

    focus_y = y + 18
    draw.rounded_rectangle((x, focus_y, card_x1 - 64, focus_y + focus_height), radius=24, fill=colors["teal"], outline=colors["teal2"], width=2)
    draw.text((x + 28, focus_y + 24), "今日重点关注", font=body_bold, fill=colors["paper"])
    fy = focus_y + 80
    for index, text in enumerate(briefing["focus"], start=1):
        draw.text((x + 28, fy), f"{index}.", font=body_bold, fill=colors["gold"])
        lines, lh, _ = paragraph(draw, text, body, content_width - 110)
        for line in lines:
            draw.text((x + 68, fy), line, font=body, fill=colors["paper"])
            fy += lh
        fy += 14

    footer_y = focus_y + focus_height + 36
    draw.text((x, footer_y), f"检索日期：{briefing['date']}｜覆盖范围：全球科技、财经与重大市场事件", font=sub, fill=colors["muted"])
    draw.text((x, footer_y + 40), "来源交叉核验：" + "｜".join(unique_sources(briefing)[:8]), font=sub, fill=colors["muted"])
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)


def first_existing_font(paths: list[str]) -> Path:
    for path in paths:
        candidate = Path(path)
        if candidate.exists():
            return candidate
    raise BriefingError("No usable font found for share image rendering.")


def unique_sources(briefing: dict[str, Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in briefing["items"]:
        for source in item["sources"]:
            if source not in seen:
                seen.add(source)
                result.append(source)
    return result


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BriefingError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
