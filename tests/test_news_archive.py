from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from news_archive import (
    archive_briefing,
    archive_path,
    archive_source_capture,
    load_archived_briefings,
    parse_briefings_js,
    read_archive,
    read_source_config,
    sources_config_to_markdown,
)


class BriefingArchiveTests(unittest.TestCase):
    def test_safe_json_only_export_parser(self):
        item = {"date": "2026-10-15", "title": "资讯", "nested": {"text": "` ${x}"}}
        self.assertEqual(parse_briefings_js("window.BRIEFINGS = " + json.dumps([item]) + ";"), [item])
        self.assertEqual(parse_briefings_js(json.dumps([item])), [item])
        self.assertEqual(parse_briefings_js('window.MORNING_BRIEFINGS = [{date: "2026-10-15", title: "a, } date: x",},];'),
                         [{"date": "2026-10-15", "title": "a, } date: x"}])
        for malicious in [
            "window.BRIEFINGS = []; fetch('https://example.com')",
            "window.BRIEFINGS = process.env",
            "window.BRIEFINGS = [Object.assign({}, {})]",
        ]:
            with self.subTest(malicious=malicious), self.assertRaises(ValueError):
                parse_briefings_js(malicious)

    def test_lossless_roundtrip_of_all_briefing_fields(self):
        item = {
            "date": "2026-10-15", "title": "标题\n````", "items": [{"what": "事件", "links": ["https://example.com"]}],
            "unknown_future_field": {"enabled": True, "value": None, "amount": 1.5},
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = archive_briefing(temporary, item, input_status="historical-input-unavailable")
            data = read_archive(path)
            self.assertEqual(data["briefing"], item)
            self.assertEqual(data["input_status"], "historical-input-unavailable")
            self.assertEqual(load_archived_briefings(temporary), [item])
            self.assertEqual(path, Path(temporary) / "archive/briefings/2026/10/2026-10-15.md")

    def test_migration_refuses_to_overwrite_different_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive_briefing(temporary, {"date": "2026-10-15", "title": "first"})
            with self.assertRaises(ValueError):
                archive_briefing(temporary, {"date": "2026-10-15", "title": "other"}, overwrite=False)

    def test_invalid_dates_and_duplicate_dates_rejected(self):
        for bad in ["../2026-10-15", "20261015", "2026-02-30", "2026-1-1"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                archive_path("/tmp", "briefings", bad)
        with self.assertRaises(ValueError):
            parse_briefings_js('[{"date":"2026-10-15"},{"date":"2026-10-15"}]')

    def test_chronological_rebuild_and_path_integrity(self):
        with tempfile.TemporaryDirectory() as temporary:
            for day in ["2026-10-14", "2026-10-15"]:
                archive_briefing(temporary, {"date": day})
            self.assertEqual([item["date"] for item in load_archived_briefings(temporary)], ["2026-10-15", "2026-10-14"])
            path = archive_path(temporary, "briefings", "2026-10-15")
            path.rename(path.with_name("2026-10-16.md"))
            with self.assertRaises(ValueError):
                load_archived_briefings(temporary)

    def test_source_capture_survives_model_failure_without_credentials(self):
        with tempfile.TemporaryDirectory() as temporary:
            item = {"source": "Test", "title": "title", "url": "https://example.com", "rss_summary": "全文摘要" * 100,
                    "published_raw": "Thu, 15 Oct 2026 00:00:00 GMT", "api_key": "SECRET", "headers": {"Authorization": "SECRET"}}
            states = [{"source": "Blocked", "url": "https://example.com/feed", "status": "failed", "http_status": 403,
                       "error_type": "HTTPError", "DASHSCOPE_API_KEY": "SECRET"}]
            path = archive_source_capture(temporary, "2026-10-15", [item], states,
                                          captured_at="2026-10-15T00:00:00+00:00", candidate_limit=30)
            # Model error happens after archiving and cannot remove these inputs.
            try:
                raise RuntimeError("model unavailable")
            except RuntimeError:
                pass
            data = read_archive(path)
            self.assertEqual(data["captures"][0]["items"][0]["rss_summary"], item["rss_summary"])
            self.assertEqual(data["captures"][0]["sources"][0]["http_status"], 403)
            self.assertNotIn("SECRET", path.read_text())
            self.assertIn("not article full text", data["content_scope"])

    def test_same_day_retries_append_but_same_capture_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            arguments = (temporary, "2026-10-15", [{"title": "headline"}], [{"status": "ok"}])
            path = archive_source_capture(*arguments, captured_at="2026-10-15T00:00:00Z")
            archive_source_capture(*arguments, captured_at="2026-10-15T00:00:00Z")
            archive_source_capture(*arguments, captured_at="2026-10-15T01:00:00Z")
            self.assertEqual(len(read_archive(path)["captures"]), 2)

    def test_all_fetched_items_are_saved_beyond_model_candidates(self):
        with tempfile.TemporaryDirectory() as temporary:
            candidates = [{"title": "first", "url": "https://example.com/first"}]
            records = candidates + [{"title": "other", "url": "https://example.com/other",
                                     "rss_description": "<p>Full RSS description</p>", "pubDate": "raw date"}]
            path = archive_source_capture(temporary, "2026-10-15", candidates, [], all_items=records)
            capture = read_archive(path)["captures"][0]
            self.assertEqual(capture["items"], records)
            self.assertEqual(capture["model_candidate_urls"], ["https://example.com/first"])

    def test_source_config_markdown_roundtrip(self):
        config = {"default_feeds": ["https://example.com/rss"], "google_news_queries": ["AI technology"], "max_candidates": 30}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.md"
            path.write_text(sources_config_to_markdown(config), encoding="utf-8")
            self.assertEqual(read_source_config(path), config)

    def test_source_config_rejects_non_http_urls_credentials_and_wrong_types(self):
        valid = {"default_feeds": ["https://example.com/rss"], "google_news_queries": ["AI technology"], "max_candidates": 30}
        for updates in [
            {"default_feeds": ["file:///etc/passwd"]},
            {"default_feeds": ["javascript:alert(1)"]},
            {"default_feeds": ["https://key:secret@example.com/rss"]},
            {"default_feeds": "https://example.com/rss"},
            {"google_news_queries": {"query": "AI"}},
            {"max_candidates": True},
            {"api_key": "SECRET"},
        ]:
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                sources_config_to_markdown({**valid, **updates})


if __name__ == "__main__":
    unittest.main()
