#!/usr/bin/env python3
"""
ChromaDB Quick Schema Checker

A lightweight script that provides a quick terminal-based overview of the ChromaDB schema
without generating visualizations. Useful for quick checks and CI/CD pipelines.
"""
import os
import sys
import json
from datetime import datetime

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def quick_schema_check():
    """Quick schema analysis without heavy dependencies"""
    import chromadb
    from chromadb.config import Settings
    
    try:
        # Set environment variables to disable telemetry
        os.environ['CHROMA_DISABLE_TELEMETRY'] = '1'
        os.environ['ANONYMIZED_TELEMETRY'] = 'False'
        
        # Get ChromaDB path
        chroma_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'chroma_storage'
        ))
        
        print("ChromaDB Quick Schema Check")
        print("=" * 40)
        print(f"Database Path: {chroma_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Initialize ChromaDB client
        try:
            client = chromadb.PersistentClient(path=chroma_path)
        except AttributeError:
            client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=chroma_path
            ))
        
        # Get all collections
        collections = client.list_collections()
        print(f"Collections Found: {len(collections)}")
        print("-" * 40)
        
        total_docs = 0
        
        for i, collection in enumerate(collections, 1):
            coll_name = collection.name
            print(f"{i}. Collection: {coll_name}")
            
            try:
                coll = client.get_collection(coll_name)
                data = coll.get()
                
                doc_count = len(data.get('ids', []))
                total_docs += doc_count
                
                print(f"   Documents: {doc_count}")
                
                # Show metadata fields
                if data.get('metadatas'):
                    all_fields = set()
                    for metadata in data['metadatas']:
                        if metadata:
                            all_fields.update(metadata.keys())
                    if all_fields:
                        print(f"   Metadata Fields: {', '.join(sorted(all_fields))}")
                    else:
                        print(f"   Metadata Fields: None")
                else:
                    print(f"   Metadata Fields: None")
                
                # Show sample IDs
                sample_ids = data.get('ids', [])[:3]
                if sample_ids:
                    print(f"   Sample IDs: {', '.join(sample_ids)}")
                
                # Document length stats
                if data.get('documents'):
                    lengths = [len(doc) if doc else 0 for doc in data['documents']]
                    if lengths:
                        print(f"   Doc Lengths: min={min(lengths)}, max={max(lengths)}, avg={sum(lengths)/len(lengths):.0f}")
                
                print()
                
            except Exception as e:
                print(f"   Error: {e}")
                print()
        
        print("-" * 40)
        print(f"Total Documents: {total_docs}")
        
        # Schema health check
        print("\nSchema Health Check:")
        if len(collections) == 0:
            print("⚠️  No collections found - database may be empty")
        elif total_docs == 0:
            print("⚠️  Collections exist but no documents found")
        else:
            print("✅ Database contains collections and documents")
            
            # Check for expected collections
            collection_names = [c.name for c in collections]
            expected_collections = ['resumes', 'jobs']
            
            for expected in expected_collections:
                if expected in collection_names:
                    print(f"✅ Expected collection '{expected}' found")
                else:
                    print(f"⚠️  Expected collection '{expected}' not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to ChromaDB: {e}")
        print("\nTroubleshooting tips:")
        print("- Ensure ChromaDB is properly installed")
        print("- Check if chroma_storage directory exists")
        print("- Verify database permissions")
        return False

def display_schema_summary():
    """Display a formatted summary if the full analysis report exists"""
    viz_dir = os.path.join(os.path.dirname(__file__), 'visualizations')
    report_path = os.path.join(viz_dir, 'chroma_schema_report.json')
    
    if os.path.exists(report_path):
        print("\n" + "=" * 50)
        print("DETAILED SCHEMA REPORT AVAILABLE")
        print("=" * 50)
        
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
            
            print(f"Last Analysis: {data.get('analysis_timestamp', 'Unknown')}")
            print(f"Total Collections: {len(data.get('collections', []))}")
            print(f"Total Documents: {data.get('total_documents', 0)}")
            print()
            
            for collection in data.get('collections', []):
                print(f"📁 {collection['name']}: {collection['document_count']} documents")
                if collection['metadata_fields']:
                    print(f"   Fields: {', '.join(collection['metadata_fields'])}")
                if collection['id_patterns']:
                    patterns = [f"{k}({v})" for k, v in collection['id_patterns'].items()]
                    print(f"   ID Patterns: {', '.join(patterns)}")
                print()
            
            print("Generated Files:")
            viz_files = [
                'chroma_overview.png',
                'document_analysis.png', 
                'metadata_analysis.png',
                'chroma_schema_report.txt'
            ]
            
            for file in viz_files:
                file_path = os.path.join(viz_dir, file)
                if os.path.exists(file_path):
                    print(f"  ✅ {file}")
                else:
                    print(f"  ❌ {file}")
            
        except Exception as e:
            print(f"Error reading detailed report: {e}")
    else:
        print(f"\n💡 Run 'python scripts/analyze_chroma_db.py' to generate detailed visualizations")

def main():
    """Main function"""
    success = quick_schema_check()
    
    if success:
        display_schema_summary()
    
    return success

if __name__ == '__main__':
    exit(0 if main() else 1)