from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.check_history import check_history, is_protected_removed_asset


def git(repo, *args):
    return subprocess.run(['git', *args], cwd=repo, check=True, capture_output=True, text=True)


def commit(repo, message):
    git(repo, 'add', '-A')
    git(repo, 'commit', '-m', message)
    return git(repo, 'rev-parse', 'HEAD').stdout.strip()


def new_repo(directory):
    repo = Path(directory)
    git(repo, 'init')
    git(repo, 'config', 'user.name', 'Test')
    git(repo, 'config', 'user.email', 'test@example.com')
    return repo


class ProtectedRemovedAssetTests(unittest.TestCase):
    def test_removed_documents_are_protected_by_name(self):
        self.assertTrue(is_protected_removed_asset('wyckoff_wti_v2.pdf'))
        self.assertTrue(is_protected_removed_asset('articoli/analisi_argomenti_futuri.md'))

    def test_instagram_pngs_are_protected(self):
        self.assertTrue(is_protected_removed_asset('articoli/petrolio_wti/instagram/Post/1.png'))
        self.assertTrue(is_protected_removed_asset('superbonus_110/instagram/01_Copertina.PNG'))

    def test_unrelated_images_and_instagram_content_are_allowed(self):
        self.assertFalse(is_protected_removed_asset('articoli/petrolio_wti/images/map.png'))
        self.assertFalse(is_protected_removed_asset('articoli/instagram/plan.md'))
        self.assertFalse(is_protected_removed_asset('assets/images/og-home.jpg'))


class IncomingHistoryTests(unittest.TestCase):
    def test_existing_pdf_history_before_base_does_not_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = new_repo(directory)
            (repo / 'Apri_Trading_in_the_Zone.pdf').write_bytes(b'legacy file')
            base = commit(repo, 'legacy PDF')
            (repo / 'Apri_Trading_in_the_Zone.pdf').unlink()
            head = commit(repo, 'remove legacy PDF')

            self.assertTrue(check_history(base=base, head=head, cwd=repo))

    def test_pdf_added_and_removed_in_incoming_commits_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = new_repo(directory)
            (repo / 'README.txt').write_text('baseline')
            base = commit(repo, 'baseline')
            (repo / 'Apri_Trading_in_the_Zone.pdf').write_bytes(b'new forbidden file')
            commit(repo, 'add forbidden PDF')
            (repo / 'Apri_Trading_in_the_Zone.pdf').unlink()
            head = commit(repo, 'remove forbidden PDF')

            self.assertFalse(check_history(base=base, head=head, cwd=repo))

    def test_initial_push_checks_all_incoming_history(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = new_repo(directory)
            (repo / 'Apri_Trading_in_the_Zone.pdf').write_bytes(b'legacy file')
            commit(repo, 'add PDF')
            (repo / 'Apri_Trading_in_the_Zone.pdf').unlink()
            head = commit(repo, 'remove PDF')

            self.assertFalse(check_history(base='0' * 40, head=head, cwd=repo))

    def test_removed_instagram_asset_added_and_removed_incoming_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = new_repo(directory)
            (repo / 'README.txt').write_text('baseline')
            base = commit(repo, 'baseline')
            image = repo / 'articoli' / 'instagram' / 'post.png'
            image.parent.mkdir(parents=True)
            image.write_bytes(b'forbidden removed image')
            commit(repo, 'add removed image')
            image.unlink()
            head = commit(repo, 'remove image')

            self.assertFalse(check_history(base=base, head=head, cwd=repo))


if __name__ == '__main__':
    unittest.main()
