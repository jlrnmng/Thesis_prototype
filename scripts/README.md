# Scripts Directory

This directory contains utility scripts for database management, migrations, and system maintenance.

## Scripts Overview

### Database Initialization
- `init_database.py` - Initialize the SQLite database schema
- `init_chroma.py` - Initialize ChromaDB vector database

### Migrations
Located in `migrations/` subdirectory:
- `add_company_fields.py` - Add company_name and company_address to users table
- `update_admin_companies.py` - Populate company names for existing admin accounts
- `migrate_add_created_by.py` - Add created_by foreign key to jobs table
- `migrate_resume_preprocessing.py` - Re-process existing resumes with new preprocessing

### Database Management
- `manage_chroma_db.py` - Manage ChromaDB collections (add, remove, query)
- `sync_chroma_db.py` - Sync SQLite data with ChromaDB
- `reset_chroma.py` - Reset ChromaDB collections
- `check_chroma_schema.py` - Verify ChromaDB schema and structure

### Data Import/Export
- `bulk_add_resumes_to_chroma.py` - Bulk import resumes to ChromaDB
- `extract_existing_resume_texts.py` - Extract text from uploaded PDF resumes
- `import_data_to_chroma.py` - Import job and resume data to vector database

### Testing & Analysis
- `test_matching.py` - Test job-resume matching algorithms
- `test_auto_sync.py` - Test automatic ChromaDB synchronization
- `test_new_preprocessing.py` - Test preprocessing on actual resumes
- `analyze_chroma_db.py` - Analyze ChromaDB contents and statistics
- `analyze_folder_structure.py` - Analyze project folder structure
- `chromadb_visualizer.py` - Visualize ChromaDB data and embeddings

### Application Checks
- `check_applications.py` - Check job application status
- `check_env.py` - Verify environment configuration
- `check_init.py` - Verify app initialization

### Job Management
- `create_test_jobs.py` - Create test job postings for development

### Cleanup
- `automated_cleanup.py` - Automated cleanup of old data
- `cleanup_analysis.py` - Analyze cleanup results

## Usage

### Running a Script
```bash
cd Hirely
python scripts/script_name.py
```

### Running Migrations
```bash
# Add company fields to database
python scripts/migrations/add_company_fields.py

# Update existing admin accounts
python scripts/migrations/update_admin_companies.py
```

### Database Initialization
```bash
# Initialize SQLite database
python scripts/init_database.py

# Initialize ChromaDB
python scripts/init_chroma.py
```

## Important Notes

⚠️ **Migrations**: Always backup your database before running migration scripts
⚠️ **Reset Scripts**: Use `reset_chroma.py` with caution - it deletes all vector data
✅ **Safe to Run**: Analysis and check scripts are read-only and safe
