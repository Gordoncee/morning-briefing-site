"""Small, dependency-free Markdown archive for the daily news pipeline.

The JSON fence in each document is its machine-readable source of truth.  No
JavaScript is evaluated, and API environment variables are never serialized.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import urllib.parse
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = 1
ITEM_FIELDS = (
    "source", "title", "url", "published", "summary", "rss_summary",
    "published_raw", "pubDate", "rss_description", "rss_content", "guid", "feed_url",
)
STATUS_FIELDS = (
    "source", "url", "status", "http_status", "feed_count", "selected_count",
    "items_count", "error_type", "reason",
)


def _date(value: str) -> str:
    """Require an ISO calendar date before constructing any filesystem path."""
    parsed = dt.date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Archive date must use YYYY-MM-DD")
    return value


def archive_path(root: str | Path, kind: str, date: str) -> Path:
    if kind not in {"briefings", "sources"}:
        raise ValueError("Unsupported archive kind")
    date = _date(date)
    return Path(root) / "archive" / kind / date[:4] / date[5:7] / f"{date}.md"


def _literal_to_json(text: str) -> str:
    """Normalize the two harmless legacy JS literal extensions, never execute.

    Early entries used bare object keys and sometimes trailing commas. Only
    those tokens outside JSON strings are changed; expressions stay invalid.
    """
    result: list[str] = []
    position = 0
    previous = ""
    decoder = json.JSONDecoder()
    while position < len(text):
        char = text[position]
        if char == '"':
            _, length = decoder.raw_decode(text[position:])
            result.append(text[position:position + length])
            position += length
            previous = '"'
            continue
        if previous in {"{", ","} and (char.isalpha() or char in {"_", "$"}):
            match = re.match(r"([A-Za-z_$][\w$]*)(\s*):", text[position:])
            if match:
                result.append(json.dumps(match.group(1)) + match.group(2) + ":")
                position += match.end()
                previous = ":"
                continue
        if char == "," and re.match(r"\s*[}\]]", text[position + 1:]):
            position += 1
            continue
        result.append(char)
        position += 1
        if not char.isspace():
            previous = char
    return "".join(result)


def parse_briefings_js(text: str) -> list[dict[str, Any]]:
    """Read JSON-compatible JS data literals without eval/exec or a JS engine."""
    text = text.lstrip("\ufeff").strip()
    assignment = re.match(
        r"(?:(?:window|globalThis)\.[A-Za-z_$][\w$]*|"
        r"(?:(?:const|let|var)\s+)?[A-Za-z_$][\w$]*)\s*=\s*",
        text,
    )
    body = _literal_to_json(text[assignment.end():] if assignment else text)
    payload, end = json.JSONDecoder().raw_decode(body)
    if body[end:].strip() not in {"", ";"}:
        raise ValueError("Unexpected executable content after briefing data")
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ValueError("Briefing data must be a JSON array of objects")
    dates = [_date(str(item.get("date", ""))) for item in payload]
    if len(dates) != len(set(dates)):
        raise ValueError("Briefing data contains duplicate dates")
    return payload


def _markdown(title: str, note: str, data: Mapping[str, Any]) -> str:
    # Compact UTF-8 JSON avoids storing another verbose copy of the content.
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return f"# {title}\n\n{note}\n\n```json\n{encoded}\n```\n"


def read_archive(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    match = re.search(r"^```json\n(.*?)\n```\s*$", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"Archive has no JSON fence: {path}")
    data = json.loads(match.group(1))
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"Unsupported archive schema: {path}")
    return data


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replacement avoids committing a partially written daily document.
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def archive_briefing(
    root: str | Path,
    briefing: Mapping[str, Any],
    *,
    input_status: str = "rss-capture-available",
    overwrite: bool = True,
) -> Path:
    date = _date(str(briefing.get("date", "")))
    if input_status not in {"rss-capture-available", "historical-input-unavailable"}:
        raise ValueError("Unsupported input status")
    path = archive_path(root, "briefings", date)
    if path.exists() and not overwrite:
        existing = read_archive(path)
        if existing.get("briefing") != dict(briefing):
            raise ValueError(f"Existing briefing differs; refusing to overwrite {path}")
        return path
    note = (
        "历史简报迁移；当时 RSS 采集输入未保存，无法还原，未补造原文。"
        if input_status == "historical-input-unavailable"
        else "完整保留已生成简报字段；当日 RSS 采集记录见 archive/sources 对应日期。"
    )
    _write(path, _markdown(f"每日资讯 · {date}", note, {
        "schema_version": SCHEMA_VERSION,
        "kind": "briefing",
        "date": date,
        "input_status": input_status,
        "briefing": dict(briefing),
    }))
    return path


def _pick(record: Mapping[str, Any], fields: Iterable[str]) -> dict[str, Any]:
    # Explicit field allowlists keep headers, tokens, clients and env out of Git.
    return {key: record[key] for key in fields if key in record}


def archive_source_capture(
    root: str | Path,
    date: str,
    items: Iterable[Mapping[str, Any]],
    statuses: Iterable[Mapping[str, Any]],
    *,
    captured_at: str | None = None,
    candidate_limit: int | None = None,
    all_items: Iterable[Mapping[str, Any]] | None = None,
    feed_records: Iterable[Mapping[str, Any]] | None = None,
) -> Path:
    """Persist the received RSS records before the (possibly failing) model call.

    Several runs on one day append separate captures. The collection only accepts
    known news/status fields: do not pass requests, API clients or environment.
    """
    date = _date(date)
    captured_at = captured_at or dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    dt.datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
    if all_items is not None and feed_records is not None:
        raise ValueError("Pass all_items or feed_records, not both")
    candidates = list(items)
    raw_items = all_items if all_items is not None else feed_records
    capture = {
        "captured_at": captured_at,
        "items": [_pick(item, ITEM_FIELDS) for item in (raw_items if raw_items is not None else candidates)],
        "sources": [_pick(status, STATUS_FIELDS) for status in statuses],
    }
    if raw_items is not None:
        capture["model_candidate_urls"] = [str(item.get("url", "")) for item in candidates]
    if candidate_limit is not None:
        if candidate_limit < 1:
            raise ValueError("Candidate limit must be positive")
        capture["candidate_limit"] = candidate_limit
    capture["capture_id"] = hashlib.sha256(
        json.dumps(capture, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:20]
    path = archive_path(root, "sources", date)
    data: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "rss-source-captures",
        "date": date,
        "content_scope": "RSS metadata and supplied summaries; not article full text",
        "captures": [],
    }
    if path.exists():
        data = read_archive(path)
        if data.get("kind") != "rss-source-captures" or data.get("date") != date:
            raise ValueError(f"Unexpected source document: {path}")
    captures = data.get("captures")
    if not isinstance(captures, list):
        raise ValueError(f"Invalid captures array: {path}")
    if not any(item.get("capture_id") == capture["capture_id"] for item in captures):
        captures.append(capture)
    _write(path, _markdown(
        f"RSS 采集记录 · {date}",
        "保存 RSS 返回的标题、链接、原始发布时间及摘要和来源请求状态；这些不是媒体文章全文。"
        "同日重试追加记录；模型失败也保留已采集输入。",
        data,
    ))
    return path


def sources_config_to_markdown(config: Mapping[str, Any]) -> str:
    config = _validate_source_config(dict(config))
    return _markdown(
        "每日资讯来源配置",
        "本文件是采集来源配置的唯一维护入口。仅保存公开 RSS 地址与搜索关键词，不保存 API 密钥。",
        {"schema_version": SCHEMA_VERSION, "kind": "source-config", "config": dict(config)},
    )


def read_source_config(path: str | Path) -> dict[str, Any]:
    data = read_archive(path)
    if data.get("kind") != "source-config" or not isinstance(data.get("config"), dict):
        raise ValueError("Expected a source-config Markdown document")
    return _validate_source_config(data["config"])


def _validate_source_config(config: dict[str, Any]) -> dict[str, Any]:
    allowed = {"default_feeds", "google_news_queries", "max_candidates"}
    if set(config) != allowed:
        raise ValueError("Source config requires only default_feeds, google_news_queries, max_candidates")
    feeds, queries, maximum = (config[key] for key in ("default_feeds", "google_news_queries", "max_candidates"))
    for name, values in (("default_feeds", feeds), ("google_news_queries", queries)):
        if not isinstance(values, list) or not values or not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError(f"{name} must be a non-empty list of strings")
        if len(values) != len(set(values)):
            raise ValueError(f"{name} contains duplicate entries")
    for url in feeds:
        if re.search(r"\s", url):
            raise ValueError("Feed URL contains whitespace")
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Feeds must use public HTTP(S) URLs without embedded credentials")
        _ = parsed.port  # Validate the port, including malformed IPv6/host forms.
    if not isinstance(maximum, int) or isinstance(maximum, bool) or not 1 <= maximum <= 200:
        raise ValueError("max_candidates must be an integer from 1 to 200")
    return config


def load_briefings(archive_dir: str | Path) -> list[dict[str, Any]]:
    """Load canonical daily documents from ROOT/archive/briefings."""
    archive_dir = Path(archive_dir)
    briefings = []
    for path in sorted(archive_dir.glob("*/*/*.md")):
        data = read_archive(path)
        if data.get("kind") != "briefing" or not isinstance(data.get("briefing"), dict):
            raise ValueError(f"Invalid briefing archive: {path}")
        date = _date(str(data["date"]))
        if archive_dir / date[:4] / date[5:7] / f"{date}.md" != path:
            raise ValueError(f"Briefing date does not match its path: {path}")
        briefing = data["briefing"]
        if briefing.get("date") != data["date"]:
            raise ValueError(f"Briefing payload date mismatch: {path}")
        briefings.append(briefing)
    return sorted(briefings, key=lambda item: item["date"], reverse=True)


def load_archived_briefings(root: str | Path) -> list[dict[str, Any]]:
    return load_briefings(Path(root) / "archive" / "briefings")
