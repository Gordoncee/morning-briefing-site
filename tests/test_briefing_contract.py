"""Regression coverage for the real Oct 29 generation/build contract failure."""
from copy import deepcopy
from datetime import date
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import generate_morning_briefing as generator
from scripts import build_news_site as builder
from scripts.briefing_schema import normalize_briefing
from scripts.news_archive import archive_briefing, archive_path, archive_source_capture, read_archive

ROOT = Path(__file__).resolve().parents[1]
STAMP = "2026-10-29"


def briefing():
    return {"date": STAMP, "displayDate": "2026年10月29日", "scope": "全球新闻｜科技与财经优先",
            "image": f"assets/morning-briefing-{STAMP}.png", "summary": "本日新闻。",
            "focus": ["科技", "财经", "AI"],
            "items": [{"title": f"新闻{i}", "region": "美国", "sources": ["Example"],
                       "summary": "新闻事实。", "why": "新闻影响。",
                       "watch": ["Azure及云收入增速", "AI相关资本开支指引"]} for i in range(3)],
            "sourceLinks": [f"https://example.org/{i}" for i in range(3)]}


class BriefingContractTests(unittest.TestCase):
    def run_generator(self, root, response=None):
        candidates = [generator.make_candidate(str(i), f"https://example.org/{i}", "RSS", "Example", "")
                      for i in range(12)]
        def collect(limit, audit):
            audit["all_items"].extend(candidates)
            return candidates
        with patch.object(generator, "ROOT", root), \
             patch.object(generator, "DATA_FILE", root / "data/briefings.js"), \
             patch.object(generator, "collect_candidates", side_effect=collect) as collect_mock, \
             patch.object(generator, "synthesize_briefing", return_value=response) as synthesize, \
             patch.object(generator, "provider_config", return_value={"model":"qwen3.8-max"}), \
             patch.object(sys, "argv", ["generate", "--date", STAMP]):
            result = generator.main()
        return result, collect_mock, synthesize

    def test_real_watch_list_is_losslessly_normalized_and_renders(self):
        raw = briefing()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.run_generator(root, deepcopy(raw))
            stored = read_archive(archive_path(root, "briefings", STAMP))["briefing"]
            self.assertEqual(stored["items"][0]["watch"], "Azure及云收入增速；AI相关资本开支指引")
            self.assertEqual(stored["sourceLinks"], raw["sourceLinks"])
            self.assertEqual(builder.validate_briefing(stored), stored)
            report = builder.build_site(root / "archive/briefings", root / "dist", ROOT / "site",
                                        builder.DEFAULT_SITE_URL, builder.DEFAULT_CASE_SITE,
                                        compatibility_root=root)
            self.assertEqual(report["latest"], STAMP)
            detail = (root / "dist" / STAMP / "index.html").read_text()
            for part in raw["items"][0]["watch"]:
                self.assertIn(part, detail)
            self.assertNotIn("['Azure", detail)
        self.assertIsInstance(raw["items"][0]["watch"], list)

    def test_existing_watch_list_repairs_archive_without_fetch_or_model(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = archive_briefing(root, briefing())
            archive_source_capture(root, STAMP, [], [])
            result, collect, synthesize = self.run_generator(root)
            self.assertEqual(result, 0)
            collect.assert_not_called()
            synthesize.assert_not_called()
            self.assertIsInstance(read_archive(path)["briefing"]["items"][0]["watch"], str)
            before = path.read_bytes()
            self.run_generator(root)
            self.assertEqual(path.read_bytes(), before)

    def test_unusable_archived_output_does_not_poison_every_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            invalid = briefing()
            invalid["items"][0]["watch"] = {"invalid": "shape"}
            archive_briefing(root, invalid)
            archive_source_capture(root, STAMP, [], [])
            result, collect, synthesize = self.run_generator(root, briefing())
            self.assertEqual(result, 0)
            collect.assert_called_once()
            synthesize.assert_called_once()
            self.assertIsInstance(read_archive(archive_path(root, "briefings", STAMP))[
                "briefing"]["items"][0]["watch"], str)

    def test_same_contract_rejects_objects_numbers_and_mixed_arrays(self):
        for field in ["summary", "why", "watch"]:
            for invalid in [{"text": "wrong"}, 42, ["valid", {"wrong":"type"}]]:
                with self.subTest(field=field, invalid=invalid):
                    raw = briefing()
                    raw["items"][0][field] = invalid
                    with self.assertRaises(generator.BriefingError):
                        generator.validate_briefing(deepcopy(raw), date.fromisoformat(STAMP))
                    with self.assertRaises(ValueError):
                        builder.validate_briefing(raw)

    def test_prose_lists_and_scalar_source_names_keep_all_content(self):
        raw = briefing()
        raw["summary"] = ["要点一", "要点二"]
        raw["items"][0].update(summary=["事实一", "事实二"], why=["影响一", "影响二"], sources="Example")
        canonical = normalize_briefing(raw)
        self.assertEqual(canonical["summary"], "要点一；要点二")
        self.assertEqual(canonical["items"][0]["summary"], "事实一；事实二")
        self.assertEqual(canonical["items"][0]["why"], "影响一；影响二")
        self.assertEqual(canonical["items"][0]["sources"], ["Example"])

    def test_invalid_model_format_gets_one_retry_then_valid_result(self):
        invalid = briefing()
        invalid["items"][0]["watch"] = {"wrong":"shape"}
        with patch.object(generator, "synthesize_briefing", side_effect=[invalid, briefing()]) as synthesize:
            result = generator.generate_valid_briefing(date.fromisoformat(STAMP), [], [])
        self.assertEqual(synthesize.call_count, 2)
        self.assertEqual(builder.validate_briefing(result), result)

    def test_repeated_invalid_model_result_is_not_archived_but_rss_survives(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            invalid = briefing()
            invalid["items"][0]["watch"] = {"wrong":"shape"}
            with self.assertRaises(generator.BriefingError):
                self.run_generator(root, invalid)
            self.assertFalse(archive_path(root, "briefings", STAMP).exists())
            self.assertEqual(len(read_archive(archive_path(root, "sources", STAMP))[
                "captures"][0]["items"]), 12)


if __name__ == "__main__":
    unittest.main()
