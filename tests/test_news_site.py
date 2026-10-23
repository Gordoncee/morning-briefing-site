"""Meaningful checks for independent Markdown-to-Pages rendering."""
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urlsplit

from scripts import build_news_site as builder
from scripts.news_archive import archive_briefing, parse_briefings_js


ROOT = Path(__file__).resolve().parents[1]


def briefing(stamp="2026-10-15", **updates):
    row = {
        "date": stamp,
        "displayDate": "2026年10月15日",
        "scope": "全球新闻｜科技与财经优先",
        "summary": "科技、财经与AI产业动向。",
        "focus": ["AI产业", "平台监管"],
        "items": [{"title": "本期新闻", "region": "美国", "sources": ["The Verge"],
                   "summary": "新闻事实摘要。", "why": "行业观察。", "watch": "后续动向。"}],
        "sourceLinks": ["https://example.com/report?from=feed&lang=en"],
        "image": f"assets/morning-briefing-{stamp}.png",
    }
    row.update(updates)
    return row


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.urls.append(value)


class NewsSiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.archive = self.root / "archive" / "briefings"
        self.output = self.root / "dist"

    def tearDown(self):
        self.temp.cleanup()

    def add_briefing(self, row):
        return archive_briefing(self.root, row)

    def build(self, **kwargs):
        return builder.build_site(self.archive, self.output, ROOT / "site",
                                  "https://example.github.io/morning-briefing-site/",
                                  "http://fazhi.cc", compatibility_root=self.root, **kwargs)

    def test_builds_every_issue_and_valid_local_links_without_database(self):
        for stamp in ["2026-10-15", "2026-10-14", "2026-09-30"]:
            self.add_briefing(briefing(stamp))
        report = self.build()
        self.assertEqual(report["pages"], 4)
        self.assertEqual(report["latest"], "2026-10-15")
        self.assertEqual(report["legacy_images"], 0)
        pages = list(self.output.rglob("*.html"))
        for page in pages:
            text = page.read_text(encoding="utf-8")
            self.assertNotIn("研究工作台", text)
            self.assertNotIn("内容管理", text)
            self.assertNotIn("查看分享图", text)
            self.assertIn('href="http://fazhi.cc/cases/">国内典型案例</a>', text)
            self.assertIn('href="http://fazhi.cc/global-cases/">全球典型案例</a>', text)
            self.assertNotIn('http://fazhi.cc/#explore', text)
            self.assertEqual(text.count('id="community-feedback"'), 1)
            self.assertIn('href="/morning-briefing-site/?v=20261023"', text)
            self.assertIn('href="http://fazhi.cc/laws/"', text)
            self.assertIn('href="http://fazhi.cc/insights/"', text)
            self.assertIn('href="http://fazhi.cc/team/"', text)
            parser = Links()
            parser.feed(text)
            for value in parser.urls:
                url = urlsplit(value)
                if url.scheme or not url.path:
                    continue
                self.assertTrue(url.path.startswith("/morning-briefing-site/"), value)
                relative = url.path.removeprefix("/morning-briefing-site/")
                target = self.output / relative
                if url.path.endswith("/"):
                    target /= "index.html"
                self.assertTrue(target.is_file(), f"Broken link in {page}: {value}")
        index = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertEqual(index.count("data-news-entry"), 3)
        self.assertIn('data-news-date="2026-10-15"', index)
        self.assertIn('data-news-month="2026-09"', index)
        self.assertIn("news-load-more", index)
        self.assertNotIn("data/briefings.js", index)
        latest = (self.output / "2026-10-15" / "index.html").read_text(encoding="utf-8")
        self.assertIn("较早一期", latest)
        self.assertNotIn("较新一期", latest)
        earliest = (self.output / "2026-09-30" / "index.html").read_text(encoding="utf-8")
        self.assertIn("较新一期", earliest)
        self.assertNotIn("较早一期", earliest)

    def test_feed_and_model_text_are_escaped_and_unsafe_links_removed(self):
        hostile = '<script>alert("feed")</script>'
        row = briefing(summary=hostile, focus=[hostile], sourceLinks=[
            "javascript:alert(1)", "data:text/html,<script>alert(1)</script>",
            "https://example.com/report?from=feed&lang=en",
        ])
        row["items"][0]["title"] = hostile
        row["items"][0]["summary"] = hostile
        self.add_briefing(row)
        self.build()
        for page in self.output.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertNotIn(hostile, text)
            self.assertNotIn("javascript:", text)
            self.assertNotIn("data:text/html", text)
            self.assertIn("&lt;script&gt;", text)
        detail = (self.output / row["date"] / "index.html").read_text(encoding="utf-8")
        self.assertIn("https://example.com/report?from=feed&amp;lang=en", detail)

    def test_rejects_wrong_dates_duplicates_and_input_directory_as_output(self):
        path = self.add_briefing(briefing())
        path.write_text(path.read_text().replace('"date":"2026-10-15"', '"date":"2026-10-16"'),
                        encoding="utf-8")
        with self.assertRaises(ValueError):
            self.build()
        path = self.add_briefing(briefing())
        duplicate = self.archive / "2026" / "09" / path.name
        duplicate.parent.mkdir(parents=True)
        duplicate.write_text(path.read_text(), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.build()
        duplicate.unlink()
        with self.assertRaises(ValueError):
            builder.build_site(self.archive, self.archive, ROOT / "site",
                               "https://example.com/", "http://fazhi.cc")
        self.assertTrue(path.exists())

    def test_share_images_are_only_opt_in(self):
        row = briefing()
        self.add_briefing(row)
        # Existing public paths stay byte-for-byte compatible, and the old
        # briefing data comes solely from Markdown, even if the old JS is bad.
        for name in builder.COMPATIBILITY_FILES:
            (self.root / name).write_text(f"legacy public file {name}\n", encoding="utf-8")
        (self.root / "data").mkdir()
        (self.root / "data" / "briefings.js").write_text("not valid javascript or JSON")
        images = self.root / "images"
        images.mkdir()
        image = images / Path(row["image"]).name
        image.write_bytes(b"existing image")
        report = self.build(legacy_images=images)
        self.assertEqual(report["legacy_images"], 1)
        for name in builder.COMPATIBILITY_FILES:
            self.assertEqual((self.output / name).read_bytes(), (self.root / name).read_bytes())
            self.assertIn(name, report["compatibility_files"])
        compact_js = (self.output / "data" / "briefings.js").read_text(encoding="utf-8")
        self.assertEqual(parse_briefings_js(compact_js), [row])
        self.assertEqual(compact_js.count("\n"), 1)
        self.assertEqual((self.output / row["image"]).read_bytes(), b"existing image")
        self.assertIn("查看分享图", (self.output / row["date"] / "index.html").read_text())


if __name__ == "__main__":
    unittest.main()
