import tempfile
import unittest
from pathlib import Path

from scripts.sync_pages import compare_pages, sync_pages


class SyncPagesTests(unittest.TestCase):
    def test_sync_updates_outputs_prunes_stale_files_and_preserves_non_site_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            site = root / '_site'
            (site / 'assets').mkdir(parents=True)
            (site / 'pagine').mkdir()
            (site / 'assets' / 'site.css').write_text('new css')
            (site / 'pagine' / 'home.html').write_text('new page')
            (site / 'index.html').write_text('new index')

            (root / 'assets').mkdir()
            (root / 'assets' / 'site.css').write_text('old css')
            (root / 'assets' / 'stale.css').write_text('stale')
            (root / 'pagine').mkdir()
            (root / 'pagine' / 'old.html').write_text('stale')
            (root / 'README.md').write_text('keep')

            errors = sync_pages(site, root)

            self.assertEqual(errors, [])
            self.assertEqual((root / 'assets' / 'site.css').read_text(), 'new css')
            self.assertFalse((root / 'assets' / 'stale.css').exists())
            self.assertFalse((root / 'pagine' / 'old.html').exists())
            self.assertEqual((root / 'README.md').read_text(), 'keep')
            self.assertEqual(compare_pages(site, root), [])

    def test_check_reports_missing_changed_stale_and_unexpected_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            site = root / '_site'
            (site / 'assets').mkdir(parents=True)
            (site / 'assets' / 'site.css').write_text('built')
            (site / 'leak.html').write_text('unexpected')
            (root / 'assets').mkdir()
            (root / 'assets' / 'site.css').write_text('different')
            (root / 'assets' / 'stale.css').write_text('stale')

            errors = compare_pages(site, root)

            self.assertIn('public output differs from build: assets/site.css', errors)
            self.assertIn('stale public output: assets/stale.css', errors)
            self.assertIn('unexpected generated path: leak.html', errors)

    def test_sync_refuses_unexpected_generated_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            site = root / '_site'
            site.mkdir()
            (site / 'leak.html').write_text('unexpected')

            errors = sync_pages(site, root)

            self.assertEqual(errors, ['unexpected generated path: leak.html'])
            self.assertFalse((root / 'leak.html').exists())


if __name__ == '__main__':
    unittest.main()
