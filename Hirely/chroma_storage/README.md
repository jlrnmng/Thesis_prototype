# ChromaDB Storage

This directory contains the ChromaDB vector database storage for Hirely's AI-powered matching system.

## Overview

ChromaDB is used to store vector embeddings of:
- 📄 **Resumes** - User resume text embeddings
- 💼 **Jobs** - Job description embeddings

These embeddings enable semantic search and similarity matching between job requirements and candidate profiles.

## Directory Structure

```
chroma_storage/
├── chroma-collections.parquet  # Collection metadata
├── chroma-embeddings.parquet   # Vector embeddings
└── index/                      # HNSW index for fast similarity search
    └── [index files]
```

## Collections

### `resumes_collection`
- **Content:** Preprocessed resume text
- **Metadata:** user_id, name, upload_date
- **Model:** all-MiniLM-L6-v2 (sentence-transformers)
- **Dimension:** 384

### `jobs_collection`
- **Content:** Preprocessed job descriptions
- **Metadata:** job_id, role, created_by, posted_date
- **Model:** all-MiniLM-L6-v2 (sentence-transformers)
- **Dimension:** 384

## How It Works

### 1. Document Addition
```python
# When a resume is uploaded
resume_text = extract_and_preprocess(pdf_file)
chroma_client.add(
    collection_name="resumes",
    documents=[resume_text],
    metadatas=[{"user_id": 123}],
    ids=["resume_123"]
)
```

### 2. Similarity Search
```python
# Find matching jobs for a resume
results = jobs_collection.query(
    query_texts=[resume_text],
    n_results=10
)
```

### 3. Hybrid Matching
Hirely uses a **hybrid approach**:
- **BM25:** Keyword-based ranking (traditional search)
- **Cosine Similarity:** Semantic matching (vector search)
- **Combined Score:** Weighted average for final ranking

## Synchronization

ChromaDB stays in sync with SQLite database through:

### Automatic Sync
- On resume upload → Add to ChromaDB
- On job posting → Add to ChromaDB
- On profile update → Update ChromaDB
- On job edit → Update ChromaDB

### Manual Sync
```bash
# Full synchronization
python scripts/sync_chroma_db.py

# Rebuild from scratch
python scripts/reset_chroma.py
python scripts/init_chroma.py
```

## Data Flow

```
User Uploads Resume (PDF)
         ↓
Extract Text (PyPDF2)
         ↓
Preprocess (177 stop words removed)
         ↓
Store in SQLite (applications table)
         ↓
Generate Embedding (sentence-transformers)
         ↓
Store in ChromaDB (chroma_storage/)
         ↓
Available for Matching
```

## Storage Size

Typical storage usage:
- **Empty:** ~2 KB (metadata only)
- **10 resumes:** ~50 KB
- **100 resumes:** ~500 KB
- **1000 resumes:** ~5 MB

*Note: Includes embeddings (384 dimensions × 4 bytes per float)*

## Maintenance

### Backup
```bash
# Create backup
cp -r chroma_storage/ chroma_storage_backup_$(date +%Y%m%d)
```

### Reset
```bash
# ⚠️ Warning: Deletes all vector data
python scripts/reset_chroma.py
```

### Verify
```bash
# Check database integrity
python scripts/analyze_chroma_db.py
```

### Rebuild
```bash
# Rebuild from SQLite data
python scripts/sync_chroma_db.py --rebuild
```

## Performance

### Query Performance
- **10 documents:** < 10ms
- **100 documents:** < 50ms
- **1000 documents:** < 200ms
- **10,000 documents:** < 1s

### Index Type
- **HNSW** (Hierarchical Navigable Small World)
- Fast approximate nearest neighbor search
- Trade-off between speed and accuracy

## Troubleshooting

### Issue: "Collection not found"
```bash
# Reinitialize ChromaDB
python scripts/init_chroma.py
```

### Issue: "Embeddings out of sync"
```bash
# Force full sync
python scripts/sync_chroma_db.py --force
```

### Issue: "Storage size too large"
```bash
# Analyze and cleanup
python scripts/analyze_chroma_db.py
python scripts/automated_cleanup.py
```

## Configuration

ChromaDB settings are in `instance/config.py`:
```python
CHROMA_PATH = 'chroma_storage'
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
CHROMA_COLLECTION_RESUMES = 'resumes_collection'
CHROMA_COLLECTION_JOBS = 'jobs_collection'
```

## Security

⚠️ **Important:**
- This directory contains **sensitive user data** (resume embeddings)
- **DO NOT** commit to public repositories
- Ensure proper `.gitignore` rules
- Backup regularly for production systems

## Related Files

- `matching_service.py` - Matching algorithm using ChromaDB
- `app/utils/chroma_sync.py` - Synchronization logic
- `scripts/init_chroma.py` - Database initialization
- `scripts/manage_chroma_db.py` - Management utilities
