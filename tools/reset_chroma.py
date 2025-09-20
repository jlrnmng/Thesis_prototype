"""
Safe ChromaDB backup & reset utility

Usage examples:
    # Dry-run backup only (default):
    python tools/reset_chroma.py

    # Backup and delete the existing chroma DB (destructive):
    python tools/reset_chroma.py --delete

    # Force delete without prompt (use with caution):
    python tools/reset_chroma.py --delete --yes

    # Use environment variable to auto-delete (same as --delete --yes):
    CHROMA_AUTO_RESET=1 python tools/reset_chroma.py

This script will:
  - locate the chroma_storage/chroma.sqlite3 relative to the project root (two levels up),
  - create a timestamped backup in chroma_storage/backups/,
  - optionally delete the original file if the user requested deletion.

It intentionally does NOT attempt to reinitialize Chroma to avoid triggering telemetry side effects.
"""

import argparse
import os
import shutil
import datetime
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CHROMA_DIR = os.path.join(PROJECT_ROOT, 'chroma_storage')
SQLITE_NAME = 'chroma.sqlite3'
SQLITE_PATH = os.path.join(CHROMA_DIR, SQLITE_NAME)
BACKUP_DIR = os.path.join(CHROMA_DIR, 'backups')


def ensure_dirs():
    if not os.path.exists(CHROMA_DIR):
        os.makedirs(CHROMA_DIR, exist_ok=True)
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)


def backup_sqlite(path: str) -> str:
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    base = os.path.basename(path)
    backup_name = f"{base}.{ts}.bak"
    dest = os.path.join(BACKUP_DIR, backup_name)
    shutil.copy2(path, dest)
    return dest


def main():
    parser = argparse.ArgumentParser(description='Backup and optionally reset ChromaDB sqlite file')
    parser.add_argument('--delete', action='store_true', help='Delete the existing chroma sqlite after backup')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation prompt (use with caution)')
    args = parser.parse_args()

    auto_reset_env = os.environ.get('CHROMA_AUTO_RESET', '0') == '1'
    delete_requested = args.delete or auto_reset_env

    print('Project root:', PROJECT_ROOT)
    print('Chroma sqlite path:', SQLITE_PATH)

    if not os.path.exists(SQLITE_PATH):
        print('No chroma sqlite file found. Nothing to do.')
        return 0

    ensure_dirs()

    try:
        backup_path = backup_sqlite(SQLITE_PATH)
        print('Backup created at:', backup_path)
    except Exception as e:
        print('Failed to create backup:', e)
        return 2

    if delete_requested:
        if not args.yes and not auto_reset_env:
            resp = input('Are you sure you want to DELETE the original chroma sqlite file? [y/N]: ').strip().lower()
            if resp not in ('y', 'yes'):
                print('Aborting deletion.')
                return 0
        try:
            os.remove(SQLITE_PATH)
            print('Original chroma sqlite removed.')
            print('Restart your application to let Chroma recreate a fresh DB.')
        except Exception as e:
            print('Failed to remove original sqlite:', e)
            return 3
    else:
        print('Deletion not requested. Backup only.')

    return 0


if __name__ == '__main__':
    sys.exit(main())
