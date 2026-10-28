import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from scripts import build_news_site as builder
from scripts import verify_news_sync as sync
from scripts.news_archive import archive_briefing
from tests.test_news_site import briefing


ROOT = Path(__file__).resolve().parents[1]


class NewsSynchronizationTests(unittest.TestCase):
    def setUp(self):
        self.expected = {"schema_version": 1, "latest": "2026-10-28", "briefings": 140,
                         "archive_sha256": "a" * 64, "navigation_version": "20261026-domain"}

    def html(self, *, page_date="", version=None, latest=None, include_card=True):
        latest = latest or self.expected["latest"]
        version = version or self.expected["archive_sha256"]
        return (f'<meta name="news-archive-version" content="{version}">'
                f'<meta name="news-latest-date" content="{latest}">'
                f'<meta name="news-page-date" content="{page_date}">'
                + (f'<a data-news-date="{latest}">News</a>' if include_card else ""))

    def matching_page(self, url, timeout):
        return self.html(page_date=self.expected["latest"] if self.expected["latest"] in url else "")

    def test_build_version_tracks_real_content_changes_on_the_same_date(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            row = briefing("2026-10-28")
            archive_briefing(root, row)
            output = root / "dist"

            def build():
                builder.build_site(root / "archive/briefings", output, ROOT / "site",
                                   builder.DEFAULT_SITE_URL, builder.DEFAULT_CASE_SITE,
                                   compatibility_root=root)
                return json.loads((output / "data/news-status.json").read_text())

            first = build()
            self.assertEqual(first, build())
            row["items"][0]["summary"] = "Same-day correction, which must reach the public page."
            archive_briefing(root, row)
            corrected = build()
            self.assertEqual(first["latest"], corrected["latest"])
            self.assertNotEqual(first["archive_sha256"], corrected["archive_sha256"])
            for filename in ["index.html", "2026-10-28/index.html"]:
                page = sync.PageMetadata()
                page.feed((output / filename).read_text())
                self.assertEqual(page.metadata["news-archive-version"], corrected["archive_sha256"])

    def test_checks_real_home_navigation_query_and_detail_on_both_origins(self):
        with patch.object(sync, "fetch_html", side_effect=self.matching_page) as fetch:
            checks = sync.check_once(self.expected, list(sync.PUBLIC_BASES))
        self.assertEqual(len(checks), 6)
        self.assertTrue(all(row["ok"] for row in checks))
        self.assertEqual(fetch.call_count, 6)
        self.assertTrue(any("fazhi.cc/news/?v=" in row["url"] for row in checks))

    def test_same_date_stale_canonical_page_fails_even_when_pages_is_current(self):
        def fetch(url, timeout):
            if "fazhi.cc" in url:
                return self.html(version="b" * 64, page_date="2026-10-28")
            return self.matching_page(url, timeout)
        with patch.object(sync, "fetch_html", side_effect=fetch):
            checks = sync.check_once(self.expected, list(sync.PUBLIC_BASES))
        self.assertTrue(all(row["ok"] for row in checks if "github.io" in row["url"]))
        self.assertTrue(all(row.get("reason") == "archive-version-mismatch"
                            for row in checks if "fazhi.cc" in row["url"]))

    def test_matching_metadata_cannot_hide_a_missing_homepage_entry_or_wrong_detail(self):
        with patch.object(sync, "fetch_html", return_value=self.html(include_card=False)):
            checks = sync.check_once(self.expected, [sync.PUBLIC_BASES[1]])
        self.assertFalse(any(row["ok"] for row in checks))
        self.assertEqual(checks[0]["reason"], "latest-briefing-missing-from-homepage")
        self.assertEqual(checks[1]["reason"], "wrong-detail-page")

    def test_today_missing_from_repository_is_not_reported_as_synchronized(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "data").mkdir()
            old = dict(self.expected, latest="2026-10-27")
            (root / "data/news-status.json").write_text(json.dumps(old))
            with self.assertRaisesRegex(ValueError, "today-briefing-missing"):
                sync.load_expected(root, "2026-10-28")

    def test_stale_cache_is_retried_and_success_requires_every_endpoint(self):
        old = [{"url": "https://fazhi.cc/news/", "ok": False}]
        new = [{"url": base, "ok": True} for base in sync.PUBLIC_BASES]
        with patch.object(sync, "check_once", side_effect=[old, new]), patch.object(sync.time, "sleep") as sleep:
            report = sync.verify_sync(self.expected, list(sync.PUBLIC_BASES), attempts=2)
        self.assertTrue(report["ok"])
        self.assertEqual(len(report["attempts"]), 2)
        sleep.assert_called_once_with(45)

    def test_exhausted_cache_or_network_failure_stays_failed_for_workflow_repair(self):
        with patch.object(sync, "fetch_html", side_effect=TimeoutError()), patch.object(sync.time, "sleep"):
            report = sync.verify_sync(self.expected, list(sync.PUBLIC_BASES), attempts=2)
        self.assertFalse(report["ok"])
        self.assertEqual(len(report["attempts"]), 2)

    def test_public_404_is_recorded_without_response_body_or_credentials(self):
        with patch.object(sync, "fetch_html", side_effect=HTTPError("https://fazhi.cc/news/", 404, "missing", {}, None)):
            checks = sync.check_once(self.expected, [sync.PUBLIC_BASES[1]])
        self.assertTrue(all(row["http_status"] == 404 and not row["ok"] for row in checks))

    def test_cli_exit_code_and_saved_report_drive_workflow_repair(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "data").mkdir()
            (root / "data/news-status.json").write_text(json.dumps(self.expected))
            report = root / "sync-report.json"
            arguments = ["verify", "--expected-dir", str(root), "--date", "2026-10-28",
                         "--attempts", "1", "--report", str(report)]
            for fetch, expected_code in [(self.matching_page, 0), (TimeoutError(), 1)]:
                with self.subTest(exit_code=expected_code), patch.object(sys, "argv", arguments), \
                     patch.object(sync, "fetch_html", side_effect=fetch):
                    self.assertEqual(sync.main(), expected_code)
                    self.assertEqual(json.loads(report.read_text())["ok"], expected_code == 0)

    def test_insecure_or_empty_public_targets_cannot_pass(self):
        for bases in [[], ["http://fazhi.cc/news/"], ["https://user:password@fazhi.cc/news/"]]:
            with self.assertRaises(ValueError), patch.object(sync, "fetch_html") as fetch:
                sync.check_once(self.expected, bases)
            fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
