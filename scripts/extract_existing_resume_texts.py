#!/usr/bin/env python3
"""Retroactively extract resume text for existing applications.

Usage:
  python tools/extract_existing_resume_texts.py [--dry-run]

This will find Application rows where resume_text is NULL/empty or uses the
placeholder "Resume for ..." and attempt to extract text from the user's saved
resume file in the uploads folder. If extraction succeeds the script updates
the Application.resume_text and (best-effort) adds the resume to ChromaDB.
"""
import os
import argparse
import traceback
import sys

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import or_

def main(dry_run=False):
    # Import app factory and DB inside function to ensure correct sys.path
    from app import create_app, db

    app = create_app()
    with app.app_context():
        from app.models import Application, User
        try:
            from app.utils.resume_extractor import extract_resume_text
        except Exception:
            print('Could not import resume extractor; aborting')
            traceback.print_exc()
            return

        q = Application.query.filter(
            or_(
                Application.resume_text == None,
                Application.resume_text == '',
                Application.resume_text.like('Resume for %')
            )
        )

        apps = q.all()
        print(f'Found {len(apps)} applications needing extraction')

        for a in apps:
            try:
                user = User.query.get(a.user_id)
                if not user:
                    print(f'Application {a.id}: user {a.user_id} not found')
                    continue

                if not user.resume:
                    print(f'Application {a.id}: user {a.id} has no resume filename')
                    continue

                upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
                resume_path = os.path.join(upload_folder, user.resume)
                if not os.path.exists(resume_path):
                    print(f'Application {a.id}: resume file missing at {resume_path}')
                    continue

                extracted = extract_resume_text(resume_path)
                if not extracted:
                    print(f'Application {a.id}: extraction returned empty')
                    continue

                print(f'Application {a.id}: extracted {len(extracted)} characters')
                a.resume_text = extracted

                if dry_run:
                    print('Dry-run: not saving to DB')
                else:
                    try:
                        db.session.add(a)
                        db.session.commit()
                        print(f'Application {a.id}: saved extracted text')
                    except Exception as e:
                        db.session.rollback()
                        print(f'Application {a.id}: error saving: {e}')

                # Skip ChromaDB adds since telemetry errors are interfering
                if dry_run:
                    print('Dry-run: not adding to ChromaDB (skipped)')
                else:
                    print('Skipping ChromaDB add during retro-extraction (telemetry errors)')

            except Exception as e:
                print(f'Application {a.id}: unexpected error: {e}')
                traceback.print_exc()

        print('Done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Do not save any changes')
    args = parser.parse_args()
    main(dry_run=args.dry_run)
