#!/usr/bin/env python3
"""Synchronize generated public files with the GitHub Pages branch/root tree."""
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'
MANAGED_DIRECTORIES = {'assets', 'articoli', 'pagine'}
MANAGED_FILES = {'.nojekyll', 'index.html', 'robots.txt', 'sitemap.xml'}


def _site_files(site):
    return {path.relative_to(site) for path in site.rglob('*') if path.is_file()}


def _managed_files(destination):
    files = set()
    for name in MANAGED_FILES:
        path = destination / name
        if path.is_file():
            files.add(Path(name))
    for name in MANAGED_DIRECTORIES:
        directory = destination / name
        if directory.is_dir():
            files.update(path.relative_to(destination) for path in directory.rglob('*') if path.is_file())
    return files


def _allowed_output(path):
    return path.as_posix() in MANAGED_FILES or path.parts[0] in MANAGED_DIRECTORIES


def compare_pages(site=SITE, destination=ROOT):
    site = Path(site).resolve()
    destination = Path(destination).resolve()
    if not site.is_dir():
        return [f'generated site directory is missing: {site}']

    expected = _site_files(site)
    errors = [f'unexpected generated path: {path.as_posix()}'
              for path in sorted(expected) if not _allowed_output(path)]
    existing = _managed_files(destination)

    for relative in sorted(expected):
        public = destination / relative
        generated = site / relative
        if not public.is_file():
            errors.append(f'missing public output: {relative.as_posix()}')
        elif public.read_bytes() != generated.read_bytes():
            errors.append(f'public output differs from build: {relative.as_posix()}')
    for relative in sorted(existing - expected):
        errors.append(f'stale public output: {relative.as_posix()}')
    return errors


def sync_pages(site=SITE, destination=ROOT):
    site = Path(site).resolve()
    destination = Path(destination).resolve()
    if not site.is_dir():
        return [f'generated site directory is missing: {site}']

    expected = _site_files(site)
    unexpected = [path for path in sorted(expected) if not _allowed_output(path)]
    if unexpected:
        return [f'unexpected generated path: {path.as_posix()}' for path in unexpected]

    for relative in sorted(expected):
        public = destination / relative
        public.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(site / relative, public)

    for relative in _managed_files(destination) - expected:
        (destination / relative).unlink()
    expected_directories = {
        parent for relative in expected for parent in relative.parents
        if parent != Path('.') and parent.parts[0] in MANAGED_DIRECTORIES
    }
    for name in MANAGED_DIRECTORIES:
        directory = destination / name
        if directory.is_dir():
            for child in sorted(directory.rglob('*'), reverse=True):
                relative = child.relative_to(destination)
                if child.is_dir() and relative not in expected_directories:
                    child.rmdir()
    return compare_pages(site, destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync generated Pages output or verify it matches.')
    parser.add_argument('--check', action='store_true', help='fail if public files differ from _site')
    args = parser.parse_args()
    errors = compare_pages() if args.check else sync_pages()
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        sys.exit(1)
    action = 'matches' if args.check else 'synchronized with'
    print(f'OK: public Pages files {action} {SITE.relative_to(ROOT)}.')
