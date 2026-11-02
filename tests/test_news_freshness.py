"""Execute the real browser update script against retained-page scenarios."""
from pathlib import Path
import shutil
import subprocess
import unittest


class NewsBrowserFreshnessTests(unittest.TestCase):
    def test_retained_browser_page_behavior(self):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node.js is required for browser regression checks; no npm packages are needed')
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([node, '--test', str(root / 'tests/news_freshness.test.cjs')],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
