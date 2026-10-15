from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import generate_morning_briefing as generator
from scripts.news_archive import archive_briefing, archive_path, archive_source_capture, read_archive


class CloudGenerationTests(unittest.TestCase):
    def test_every_configured_source_is_archived_without_changing_model_quota(self):
        calls = []
        def fetch(url, status):
            calls.append(url)
            status.update(status='ok', items_count=10)
            return [generator.make_candidate(f'{url}-{i}', f'https://example.org/{len(url)}/{i}/{url}',
                                              'x' * 400, 'Example', '') for i in range(10)]
        audit = {'statuses': [], 'all_items': []}
        with patch.object(generator, 'fetch_feed', side_effect=fetch):
            candidates = generator.collect_candidates(30, audit)
        self.assertEqual(len(calls), 13)
        self.assertEqual(len(audit['statuses']), 13)
        self.assertEqual(len(audit['all_items']), 130)
        self.assertEqual(len(candidates), 30)
        self.assertEqual([x['selected_count'] for x in audit['statuses']], [7,7,7,7,2,0,0,0,0,0,0,0,0])
        self.assertEqual(len(candidates[0]['summary']), 220)
        self.assertEqual(len(audit['all_items'][0]['rss_summary']), 400)
        self.assertNotIn('rss_summary', candidates[0])

    def test_model_failure_keeps_source_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rows = [generator.make_candidate(f'Title {i}', f'https://example.org/{i}', 'raw summary', 'Example', '') for i in range(12)]
            def collect(limit, audit):
                audit['statuses'].append({'url': 'https://example.org/rss', 'status': 'ok', 'items_count': 12})
                audit['all_items'].extend(rows)
                return rows
            with patch.object(generator, 'ROOT', root), patch.object(generator, 'DATA_FILE', root/'data/briefings.js'), \
                 patch.object(generator, 'collect_candidates', side_effect=collect), \
                 patch.object(generator, 'synthesize_briefing', side_effect=generator.BriefingError('failure')), \
                 patch.object(sys, 'argv', ['generate', '--date', '2026-10-15']):
                with self.assertRaises(generator.BriefingError): generator.main()
            path = archive_path(root, 'sources', '2026-10-15')
            self.assertEqual(len(read_archive(path)['captures'][0]['items']), 12)
            self.assertFalse(archive_path(root, 'briefings', '2026-10-15').exists())

    def test_successful_date_is_idempotent_and_does_not_call_model(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_briefing(root, {'date':'2026-10-15','items':[],'sourceLinks':[]})
            archive_source_capture(root, '2026-10-15', [], [])
            with patch.object(generator, 'ROOT', root), patch.object(generator, 'DATA_FILE', root/'data/briefings.js'), \
                 patch.object(generator, 'collect_candidates') as collect, \
                 patch.object(generator, 'synthesize_briefing') as synthesize, \
                 patch.object(sys, 'argv', ['generate', '--date', '2026-10-15']):
                self.assertEqual(generator.main(), 0)
            collect.assert_not_called()
            synthesize.assert_not_called()
            self.assertTrue((root/'data/briefings.js').exists())

    def test_recent_history_reads_quoted_keys_from_canonical_markdown(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for stamp in ['2026-10-14','2026-10-15']:
                archive_briefing(root, {'date':stamp,'items':[{'title':stamp}], 'sourceLinks':[f'https://example.org/{stamp}']})
            with patch.object(generator, 'ROOT', root):
                recent = generator.load_existing_briefings(root/'missing.js')[0]
            self.assertEqual(recent['dates'], ['2026-10-15','2026-10-14'])
            self.assertEqual(recent['titles'][0], '2026-10-15')

if __name__ == '__main__': unittest.main()
