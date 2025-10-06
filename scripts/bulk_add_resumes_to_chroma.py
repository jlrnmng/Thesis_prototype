#!/usr/bin/env python3
"""Bulk add resumes to ChromaDB from existing Application records.

Usage:
  python tools/bulk_add_resumes_to_chroma.py [--dry-run]

This will find all Application records with non-empty resume_text and
add them to ChromaDB for matching. Uses improved error handling to
work around telemetry issues.
"""
import os
import sys
import argparse
import traceback

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main(dry_run=False):
    # Import app factory and DB inside function to ensure correct sys.path
    from app import create_app, db
    from matching_service import get_matching_service

    app = create_app()
    with app.app_context():
        from app.models import Application

        # Get all applications with non-empty resume text
        apps = Application.query.filter(
            Application.resume_text.isnot(None),
            Application.resume_text != '',
            ~Application.resume_text.like('Resume for %')  # Exclude placeholders
        ).all()

        print(f'Found {len(apps)} applications with resume text')

        # Initialize ChromaDB client with minimal config and telemetry disabled
        os.environ['CHROMA_DISABLE_TELEMETRY'] = '1'
        import chromadb
        from chromadb.utils import embedding_functions
        from sentence_transformers import SentenceTransformer

        chroma_path = app.config.get('CHROMA_PATH', 'chroma_storage')
        client = chromadb.PersistentClient(path=chroma_path)
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        try:
            collection = client.get_collection(name="resumes", embedding_function=embedding_fn)
        except:
            collection = client.create_collection(name="resumes", embedding_function=embedding_fn)

        success = 0
        for a in apps:
            try:
                if dry_run:
                    print(f'Application {a.id}: would add to ChromaDB (dry run)')
                    continue

                collection.upsert(
                    documents=[a.resume_text],
                    ids=[f"user_{a.user_id}"],
                    metadatas=[{"user_id": a.user_id}]
                )
                print(f'Application {a.id}: successfully added to ChromaDB')
                success += 1

            except Exception as e:
                print(f'Application {a.id}: unexpected error: {e}')
                traceback.print_exc()

        print(f'\nSummary:')
        print(f'Total applications processed: {len(apps)}')
        if not dry_run:
            print(f'Successfully added to ChromaDB: {success}')
            print(f'Failed to add: {len(apps) - success}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                   formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dry-run', action='store_true',
                       help="Don't save changes, just show what would be done")
    args = parser.parse_args()
    main(args.dry_run)