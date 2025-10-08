#!/usr/bin/env python3
"""
Migrate existing resume text data to include NLP preprocessing.

This script will:
1. Find all Application records with resume_text
2. Apply NLP preprocessing to the text
3. Update the database with preprocessed text
4. Optionally backup original text

Usage:
  python scripts/migrate_resume_preprocessing.py [--dry-run] [--backup]
"""
import os
import sys
import argparse
from datetime import datetime

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main(dry_run=False, backup=False):
    from app import create_app, db
    
    app = create_app()
    with app.app_context():
        from app.models import Application
        
        # Import preprocessing utilities
        try:
            from app.utils.text_preprocessing import preprocess_resume_text
            print('Text preprocessing module loaded successfully')
        except ImportError:
            print('Error: Text preprocessing module not available')
            return
        except Exception as e:
            print(f'Error: Failed to load preprocessing module: {e}')
            return
        
        # Get all applications with resume text
        apps = Application.query.filter(
            Application.resume_text.isnot(None),
            Application.resume_text != '',
            ~Application.resume_text.like('Resume for %')  # Exclude placeholders
        ).all()
        
        print(f'Found {len(apps)} applications with resume text to process')
        
        if backup:
            backup_file = f'resume_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            print(f'Creating backup file: {backup_file}')
        
        processed = 0
        errors = 0
        
        for app in apps:
            try:
                original_text = app.resume_text
                original_length = len(original_text)
                
                # Apply preprocessing
                processed_text = preprocess_resume_text(original_text, for_matching=False)
                processed_length = len(processed_text)
                
                # Check if preprocessing made a meaningful change
                if processed_text != original_text:
                    if backup and not dry_run:
                        # Write backup entry
                        with open(backup_file, 'a', encoding='utf-8') as f:
                            f.write(f"=== Application ID: {app.id} ===\n")
                            f.write(f"Original ({original_length} chars):\n")
                            f.write(original_text)
                            f.write(f"\n\nProcessed ({processed_length} chars):\n")
                            f.write(processed_text)
                            f.write("\n" + "="*50 + "\n\n")
                    
                    if dry_run:
                        print(f'App {app.id}: would update ({original_length} -> {processed_length} chars)')
                    else:
                        app.resume_text = processed_text
                        print(f'App {app.id}: updated ({original_length} -> {processed_length} chars)')
                        processed += 1
                else:
                    print(f'App {app.id}: no changes needed')
                
            except Exception as e:
                print(f'App {app.id}: preprocessing error - {e}')
                errors += 1
        
        if not dry_run and processed > 0:
            try:
                db.session.commit()
                print(f'\nSuccessfully committed {processed} updates to database')
            except Exception as e:
                print(f'\nError committing to database: {e}')
                db.session.rollback()
        
        print(f'\nSummary:')
        print(f'Total applications: {len(apps)}')
        print(f'Successfully processed: {processed}')
        print(f'Errors: {errors}')
        if backup and not dry_run:
            print(f'Backup saved to: {backup_file}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                   formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dry-run', action='store_true',
                       help="Show what would be changed without making updates")
    parser.add_argument('--backup', action='store_true',
                       help="Create backup file with original and processed text")
    
    args = parser.parse_args()
    main(args.dry_run, args.backup)