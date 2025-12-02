# Instance Directory

This directory contains instance-specific configuration and database files for the Hirely application.

## Overview

The `instance/` folder stores configuration and data that is **specific to each deployment** of the application. This includes database files, secret keys, and environment-specific settings.

## Directory Contents

```
instance/
├── config.py              # Application configuration (DO NOT COMMIT)
├── resume_matcher.db      # SQLite database file
└── *.log                  # Application log files (if any)
```

## Configuration File (`config.py`)

**Purpose:** Store environment-specific settings

**Typical Contents:**
```python
# Database Configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/resume_matcher.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Security
SECRET_KEY = 'your-secret-key-here'  # ⚠️ Change in production!
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Upload Configuration
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
ALLOWED_EXTENSIONS = {'pdf'}

# ChromaDB Configuration
CHROMA_PATH = 'chroma_storage'
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

# Session Configuration
PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
SESSION_TIMEOUT_WARNING = 300      # 5 minutes warning

# Application Settings
DEBUG = False  # Set to True for development
TESTING = False
```

## Database File (`resume_matcher.db`)

**Type:** SQLite3 database

**Tables:**
- `users` - User accounts (job seekers and admins)
- `jobs` - Job postings
- `applications` - Job applications with resume text

**Schema:**

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    middle_name VARCHAR(80),
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(30),
    address TEXT,
    password_hash VARCHAR(128),
    resume VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    company_name VARCHAR(200),      -- For admins
    company_address TEXT,            -- For admins
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Jobs Table
```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    role VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    cluster_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER NOT NULL,    -- Foreign key to users.id
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### Applications Table
```sql
CREATE TABLE applications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    cluster_id INTEGER,
    resume_text TEXT NOT NULL,
    submission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    UNIQUE(user_id, job_id)  -- Prevent duplicate applications
);
```

## Security Best Practices

### ⚠️ DO NOT:
- ❌ Commit `config.py` with secret keys to Git
- ❌ Share database files publicly
- ❌ Use default SECRET_KEY in production
- ❌ Commit files with user PII (Personally Identifiable Information)

### ✅ DO:
- ✅ Use environment variables for secrets
- ✅ Backup database regularly
- ✅ Use strong SECRET_KEY (64+ random characters)
- ✅ Restrict file permissions (chmod 600)
- ✅ Use `.gitignore` for instance folder

## .gitignore Configuration

```gitignore
# Instance folder - DO NOT commit sensitive data
instance/config.py
instance/*.log

# Database options (choose one approach):

# Option 1: Share database with team (current)
# (Database file is committed for development)

# Option 2: Each developer creates their own database
# Uncomment to exclude database:
# instance/*.db
# instance/*.sqlite3
```

## Development vs Production

### Development
```python
# instance/config.py (development)
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/resume_matcher.db'
SECRET_KEY = 'dev-secret-key'  # OK for development
```

### Production
```python
# instance/config.py (production)
import os

DEBUG = False
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')  # From environment
SESSION_COOKIE_SECURE = True  # HTTPS only
```

## Database Management

### Initialize Database
```bash
# Create tables
python scripts/init_database.py
```

### Backup Database
```bash
# Create backup with timestamp
cp instance/resume_matcher.db instance/resume_matcher_backup_$(date +%Y%m%d).db
```

### Reset Database
```bash
# ⚠️ Warning: Deletes all data
rm instance/resume_matcher.db
python scripts/init_database.py
```

### View Database
```bash
# Using SQLite command line
sqlite3 instance/resume_matcher.db

# Example queries
sqlite> SELECT COUNT(*) FROM users;
sqlite> SELECT COUNT(*) FROM jobs;
sqlite> SELECT COUNT(*) FROM applications;
sqlite> .quit
```

### Migrations
```bash
# Run database migrations
python scripts/migrations/add_company_fields.py
python scripts/migrations/update_admin_companies.py
```

## File Permissions

Recommended permissions:
```bash
chmod 700 instance/           # Only owner can read/write/execute
chmod 600 instance/config.py  # Only owner can read/write
chmod 644 instance/resume_matcher.db  # Owner rw, group r, others r
```

## Troubleshooting

### Issue: "Database is locked"
```bash
# Check for other processes using the database
lsof instance/resume_matcher.db

# Or restart the application
```

### Issue: "Config not found"
```bash
# Create default config
cp instance/config.example.py instance/config.py
# Edit with your settings
```

### Issue: "Permission denied"
```bash
# Fix file permissions
chmod 600 instance/config.py
chmod 644 instance/resume_matcher.db
```

## Environment Variables (Production)

Instead of `config.py`, use environment variables:

```bash
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:pass@host/db"
export FLASK_ENV="production"
```

Then in `config.py`:
```python
import os

SECRET_KEY = os.environ.get('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/resume_matcher.db')
```

## Related Files

- `app/__init__.py` - Loads instance config
- `app/models.py` - Database models
- `scripts/init_database.py` - Database initialization
- `scripts/migrations/` - Database migration scripts
