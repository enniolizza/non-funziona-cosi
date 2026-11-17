#!/usr/bin/env python3
"""Block protected assets in the current tree or commits incoming since the base."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REMOVED_PATH = 'Apri_Trading_in_the_Zone.pdf'
REMOVED_BLOB = 'f1297c62a800a2bb74b2c15130f1f3f0668a0d32'
REMOVED_FILENAMES = {'wyckoff_wti_v2.pdf', 'analisi_argomenti_futuri.md'}


def is_protected_removed_asset(path):
    normalized = path.replace('\\', '/').casefold()
    parts = normalized.split('/')
    return (parts[-1] in REMOVED_FILENAMES or
            ('instagram' in parts and parts[-1].endswith('.png')))


def git_paths(args, cwd=ROOT):
    result = subprocess.run(['git', *args], cwd=cwd, capture_output=True, check=True)
    return [path.decode('utf-8', errors='surrogateescape')
            for path in result.stdout.split(b'\0') if path]


def git_tree_entries(head, cwd=ROOT):
    result = subprocess.run(['git', 'ls-tree', '-r', '-z', head], cwd=cwd,
                            capture_output=True, check=True)
    entries = []
    for entry in result.stdout.split(b'\0'):
        if entry:
            metadata, path = entry.split(b'\t', 1)
            oid = metadata.split()[2].decode('ascii')
            entries.append((oid, path.decode('utf-8', errors='surrogateescape')))
    return entries


def check_history(base=None, head='HEAD', cwd=ROOT):
    initial_push = bool(base and set(base) == {'0'})
    if initial_push:
        base = None

    if base or initial_push:
        shallow = subprocess.run(['git', 'rev-parse', '--is-shallow-repository'], cwd=cwd,
                                 text=True, capture_output=True, check=True)
        if shallow.stdout.strip() == 'true':
            raise ValueError('A complete clone is required to inspect incoming history.')

        revision_range = f'{base}..{head}' if base else head
        result = subprocess.run(['git', 'rev-list', '--objects', revision_range], cwd=cwd,
                                text=True, capture_output=True, check=True)
        for line in result.stdout.splitlines():
            oid, _, path = line.partition(' ')
            if (oid == REMOVED_BLOB or Path(path).name == REMOVED_PATH or
                    (path and is_protected_removed_asset(path))):
                return False

    head_entries = git_tree_entries(head, cwd=cwd)
    if any(oid == REMOVED_BLOB or Path(path).name == REMOVED_PATH or
           is_protected_removed_asset(path) for oid, path in head_entries):
        return False
    if base:
        incoming_paths = git_paths([
            'diff', '--name-only', '--diff-filter=ACMRT', '--no-renames', '-z', base, head,
        ], cwd=cwd)
        if any(is_protected_removed_asset(path) for path in incoming_paths):
            return False
    return True


if __name__ == '__main__':
    try:
        clean = check_history(base=os.environ.get('BASE_SHA'),
                              head=os.environ.get('HEAD_SHA', 'HEAD'))
    except (subprocess.CalledProcessError, ValueError):
        print('ERROR: Git history unavailable; use a complete clone.', file=sys.stderr)
        sys.exit(1)
    if not clean:
        print('ERROR: a protected removed asset is present in HEAD or in commits incoming from BASE_SHA.',
              file=sys.stderr)
        sys.exit(1)
    if os.environ.get('BASE_SHA'):
        print('OK: protected removed assets are absent from HEAD and incoming commits.')
    else:
        print('OK: protected removed assets are absent from HEAD (BASE_SHA not set; incoming history was not checked).')
