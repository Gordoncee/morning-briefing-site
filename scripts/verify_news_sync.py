#!/usr/bin/env python3
"""Check that real public HTML matches the Markdown archive used for this build.

Only public pages are read. No model, SSH access, credentials, server-side task,
or cache-busting URL is needed. Repeated normal reads allow the existing proxy's
five-minute cache and background refresh to catch up.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

PUBLIC_BASES = ("https://gordoncee.github.io/morning-briefing-site/", "https://fazhi.cc/news/")


class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.metadata = {}
        self.dates = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name", "").startswith("news-"):
            self.metadata[attrs["name"]] = attrs.get("content", "")
        if attrs.get("data-news-date"):
            self.dates.add(attrs["data-news-date"])


def fetch_html(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": "fazhi-news-sync-check/1.0",
                                    "Cache-Control": "no-cache"})
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError("unexpected-http-status")
        content = response.read(2 * 1024 * 1024 + 1)
        if len(content) > 2 * 1024 * 1024:
            raise ValueError("page-too-large")
        return content.decode("utf-8")


def load_expected(directory: Path, required_date: str) -> dict:
    expected = json.loads((directory / "data" / "news-status.json").read_text(encoding="utf-8"))
    if expected.get("schema_version") != 1:
        raise ValueError("unsupported-sync-manifest")
    latest = dt.date.fromisoformat(expected["latest"]).isoformat()
    if latest < dt.date.fromisoformat(required_date).isoformat():
        raise ValueError("today-briefing-missing-from-repository")
    if not re.fullmatch(r"[0-9a-f]{64}", expected.get("archive_sha256", "")):
        raise ValueError("invalid-archive-version")
    return expected


def check_once(expected: dict, bases: list[str], timeout: float = 12) -> list[dict]:
    if not bases:
        raise ValueError("at-least-one-public-entry-required")
    targets = []
    for base in bases:
        parts = urlsplit(base)
        if parts.scheme != "https" or not parts.netloc or parts.query or parts.fragment or parts.username:
            raise ValueError("public-base-must-be-a-clean-https-url")
        base = base.rstrip("/") + "/"
        targets.extend([(base, "home"), (base + expected["latest"] + "/", "detail")])
        if expected.get("navigation_version"):
            targets.append((base + "?" + urlencode({"v": expected["navigation_version"]}), "home"))

    def check(target):
        url, kind = target
        result = {"url": url, "ok": False}
        try:
            page = PageMetadata()
            page.feed(fetch_html(url, timeout))
            result["observed_latest"] = page.metadata.get("news-latest-date")
            if page.metadata.get("news-archive-version") != expected["archive_sha256"]:
                result["reason"] = "archive-version-mismatch"
            elif result["observed_latest"] != expected["latest"]:
                result["reason"] = "latest-date-mismatch"
            elif kind == "home" and expected["latest"] not in page.dates:
                result["reason"] = "latest-briefing-missing-from-homepage"
            elif kind == "detail" and page.metadata.get("news-page-date") != expected["latest"]:
                result["reason"] = "wrong-detail-page"
            else:
                result["ok"] = True
        except (OSError, ValueError) as error:
            result["reason"] = type(error).__name__
            if hasattr(error, "code"):
                result["http_status"] = error.code
        return result

    with ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(check, targets))


def verify_sync(expected: dict, bases: list[str], attempts: int = 8,
                delay: float = 45, timeout: float = 12) -> dict:
    report = {"ok": False, "expected_latest": expected["latest"],
              "archive_sha256": expected["archive_sha256"], "attempts": []}
    for number in range(1, attempts + 1):
        checks = check_once(expected, bases, timeout)
        report["attempts"].append({"number": number, "checks": checks})
        report["ok"] = all(row["ok"] for row in checks)
        print(json.dumps({"attempt": number, "ok": report["ok"], "checks": checks}, ensure_ascii=False), flush=True)
        if report["ok"]:
            break
        if number < attempts:
            time.sleep(delay)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-dir", type=Path, default=Path("dist"))
    parser.add_argument("--date", default=os.environ.get("BRIEFING_DATE", ""))
    parser.add_argument("--base", action="append", help="Public HTTPS base; defaults to both live entries")
    parser.add_argument("--attempts", type=int, default=8)
    parser.add_argument("--delay", type=float, default=45)
    parser.add_argument("--timeout", type=float, default=12)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not 1 <= args.attempts <= 12 or not 0 <= args.delay <= 90 or not 0 < args.timeout <= 30:
        parser.error("check attempts, delay and timeout bounds")
    stamp = args.date or dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat()
    try:
        expected = load_expected(args.expected_dir, stamp)
        report = verify_sync(expected, args.base or list(PUBLIC_BASES), args.attempts, args.delay, args.timeout)
    except (OSError, ValueError, KeyError) as error:
        report = {"ok": False, "required_date": stamp, "error": str(error)}
        print(json.dumps(report, ensure_ascii=False), flush=True)
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
