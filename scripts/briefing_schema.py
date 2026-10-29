"""Shared content contract for model generation and static publication.

Lists of prose are joined without dropping any text. Objects, numbers and mixed
lists are rejected rather than converted into misleading public strings.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date


def text(value: object, label: str) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list) and all(isinstance(part, str) for part in value):
        return "；".join(part.strip() for part in value if part.strip())
    raise ValueError(f"{label} must be text or an array of text")


def strings(value: object, label: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be an array of strings")
    return value


def normalize_briefing(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Briefing metadata must be an object")
    row = deepcopy(payload)
    label = f"Briefing {row.get('date', 'unknown')}"
    stamp = row.get("date", "")
    if not isinstance(stamp, str):
        raise ValueError(f"{label}: date must use YYYY-MM-DD")
    parsed = date.fromisoformat(stamp)
    if parsed.isoformat() != stamp:
        raise ValueError(f"{label}: date must use YYYY-MM-DD")
    for field in ("scope", "displayDate", "image"):
        if field in row and not isinstance(row[field], str):
            raise ValueError(f"{label}: {field} must be a string")
    row.setdefault("displayDate", f"{parsed.year}年{parsed.month}月{parsed.day}日")
    row.setdefault("scope", "全球新闻｜科技与财经优先")
    row["summary"] = text(row.get("summary", ""), f"{label}: summary")
    for field in ("focus", "sourceLinks"):
        row[field] = strings(row.get(field), f"{label}: {field}")
    if not isinstance(row.get("items"), list) or not row["items"]:
        raise ValueError(f"{label}: items must be a non-empty array")
    for item in row["items"]:
        if not isinstance(item, dict):
            raise ValueError(f"{label}: each item must be an object")
        if not isinstance(item.get("title"), str) or not item["title"].strip():
            raise ValueError(f"{label}: each item needs a non-empty title")
        item["summary"] = text(item.get("summary"), f"{label}: item summary")
        if not item["summary"].strip():
            raise ValueError(f"{label}: each item needs a non-empty summary")
        if not isinstance(item.get("region", ""), str):
            raise ValueError(f"{label}: item region must be a string")
        for field in ("why", "watch"):
            # Preserve absent optional fields in historical entries.
            if field in item:
                item[field] = text(item[field], f"{label}: item {field}")
        item["sources"] = strings(item.get("sources"), f"{label}: item sources")
    return row
