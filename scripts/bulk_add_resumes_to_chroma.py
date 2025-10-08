#!/usr/bin/env python3
"""Bulk add resumes to ChromaDB from existing Application records with NLP preprocessing.

Usage:
  python scripts/bulk_add_resumes_to_chroma.py [--dry-run] [--preprocess]

This will find all Application records with non-empty resume_text and
add them to ChromaDB for matching. Uses improved error handling to
work around telemetry issues. Now includes optional NLP preprocessing
for better matching performance.
"""
import os
import sys
import argparse
import traceback

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main(dry_run=False, preprocess=True):
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
        if preprocess:
            print('NLP preprocessing enabled for better matching performance')
            
        # Try to import preprocessing utilities
        preprocess_func = None
        if preprocess:
            try:
                from app.utils.text_preprocessing import preprocess_resume_text
                preprocess_func = preprocess_resume_text
                print('Text preprocessing module loaded successfully')
            except ImportError:
                print('Warning: Text preprocessing module not available, using raw text')
                preprocess = False
            except Exception as e:
                print(f'Warning: Error loading preprocessing module: {e}, using raw text')
                preprocess = False

        # Initialize ChromaDB client with improved compatibility
        os.environ['CHROMA_DISABLE_TELEMETRY'] = '1'
        import chromadb
        from chromadb.utils import embedding_functions
        from sentence_transformers import SentenceTransformer

        chroma_path = app.config.get('CHROMA_PATH', 'chroma_storage')
        
        # Try different ChromaDB client initialization methods for compatibility
        try:
            # Try the new API first
            if hasattr(chromadb, 'PersistentClient'):
                client = chromadb.PersistentClient(path=chroma_path)
            else:
                # Fallback to older API
                import chromadb.config
                client = chromadb.Client(chromadb.config.Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=chroma_path
                ))
        except Exception as e:
            print(f"ChromaDB initialization error: {e}")
            # Final fallback - use in-memory client
            client = chromadb.Client()
            
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
                # Apply preprocessing if enabled
                resume_text = a.resume_text
                if preprocess and preprocess_func:
                    try:
                        processed_text = preprocess_func(resume_text, for_matching=False)
                        resume_text = processed_text
                        print(f'Application {a.id}: applied NLP preprocessing (length: {len(a.resume_text)} -> {len(processed_text)})')
                    except Exception as e:
                        print(f'Application {a.id}: preprocessing failed ({e}), using original text')
                
                if dry_run:
                    print(f'Application {a.id}: would add to ChromaDB (dry run)')
                    continue

                collection.upsert(
                    documents=[resume_text],
                    ids=[f"user_{a.user_id}"],
                    metadatas=[{"user_id": a.user_id, "preprocessed": preprocess}]
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
    parser.add_argument('--preprocess', action='store_true', default=True,
                       help="Apply NLP preprocessing to resume text (default: True)")
    parser.add_argument('--no-preprocess', action='store_false', dest='preprocess',
                       help="Skip NLP preprocessing and use raw text")
    args = parser.parse_args()
    main(args.dry_run, args.preprocess)