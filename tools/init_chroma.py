#!/usr/bin/env python3
"""Initialize and verify ChromaDB collections.

This script ensures ChromaDB is properly set up with all required collections
and schema. It will:
1. Create the ChromaDB directory if it doesn't exist
2. Initialize the database with required tables
3. Create required collections (resumes and jobs)
4. Verify the collections are accessible
"""
import os
import sys
import shutil
from datetime import datetime

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def backup_db(chroma_path):
    """Create backup of existing ChromaDB if it exists"""
    db_path = os.path.join(chroma_path, 'chroma.sqlite3')
    if os.path.exists(db_path):
        backup_dir = os.path.join(chroma_path, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        backup_path = os.path.join(backup_dir, f'chroma.sqlite3.{timestamp}.bak')
        shutil.copy2(db_path, backup_path)
        print(f"Created backup at: {backup_path}")

def clean_chroma_dir(chroma_path):
    """Clean up ChromaDB directory while preserving backups"""
    # Backup existing DB
    backup_db(chroma_path)
    
    # Remove all files except backups directory
    for item in os.listdir(chroma_path):
        item_path = os.path.join(chroma_path, item)
        if item != 'backups' and os.path.exists(item_path):
            if os.path.isfile(item_path):
                os.unlink(item_path)
            else:
                shutil.rmtree(item_path)
    print("Cleaned ChromaDB directory")

def init_chroma():
    """Initialize ChromaDB with required collections"""
    from app import create_app
    import chromadb
    from chromadb.utils import embedding_functions
    from chromadb.config import Settings
    import sqlite3
    import time
    
    # Set all possible telemetry and tracking to false
    os.environ['CHROMA_DISABLE_TELEMETRY'] = '1'
    os.environ['ANONYMIZED_TELEMETRY'] = 'False'
    os.environ['POSTHOG_API_KEY'] = ''
    
    app = create_app()
    
    with app.app_context():
        # Use an absolute path in the standard location
        chroma_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..',
            'chroma_storage'
        ))
        print(f"\nInitializing new ChromaDB at: {chroma_path}")
        
        # Remove the new directory if it exists
        if os.path.exists(chroma_path):
            shutil.rmtree(chroma_path)
        
        # Create fresh directory
        os.makedirs(chroma_path)
        
        # Update app config to use new path
        app.config['CHROMA_PATH'] = chroma_path
        
        # Initialize client with older, stable API
        try:
            client = chromadb.Client(chromadb.config.Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=chroma_path
            ))
            print("ChromaDB client initialized successfully")
        except Exception as e:
            print(f"Error initializing ChromaDB client: {e}")
            return False
            
        # Set up embedding function
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or get collections
        try:
            resumes_collection = client.create_collection(
                name="resumes",
                embedding_function=embedding_fn,
                get_or_create=True
            )
            print("'resumes' collection initialized")
            
            jobs_collection = client.create_collection(
                name="jobs",
                embedding_function=embedding_fn,
                get_or_create=True
            )
            print("'jobs' collection initialized")
        except Exception as e:
            print(f"Error creating collections: {e}")
            return False
            
        # Verify collections are queryable
        try:
            resumes = client.get_collection("resumes")
            jobs = client.get_collection("jobs")
            print("\nVerifying collections:")
            print(f"- Resumes collection: {len(resumes.get()['ids'])} documents")
            print(f"- Jobs collection: {len(jobs.get()['ids'])} documents")
        except Exception as e:
            print(f"Error verifying collections: {e}")
            return False
            
        return True

if __name__ == '__main__':
    if init_chroma():
        print("\nChromaDB initialized successfully!")
    else:
        print("\nFailed to initialize ChromaDB")