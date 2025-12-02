# Utils Directory

This directory contains utility modules and helper functions used throughout the Hirely application.

## Modules Overview

### 🔒 Security (`security.py`)
**Purpose:** Session security, CSRF protection, and secure route handling

**Key Functions:**
- `secure_route()` - Decorator for protected routes with session validation
- `session_security_check()` - Validates session integrity and timeout
- `check_session_timeout()` - Monitors session expiration
- `invalidate_session()` - Securely clears session data
- `log_security_event()` - Audit logging for security events

**Features:**
- Session timeout management (30 minutes default)
- Cache prevention headers
- CSRF token validation
- User agent validation
- IP address tracking

---

### 🎨 Decorators (`decorators.py`)
**Purpose:** Custom route decorators for common functionality

**Decorators:**
- `@secure_route` - Comprehensive security wrapper
- `@admin_required` - Restricts access to admin users only
- `@login_required` - Ensures user is authenticated

**Usage:**
```python
@app.route('/protected')
@secure_route
def protected_route():
    return "Secure content"
```

---

### 📄 PDF Processor (`pdf_processor.py`)
**Purpose:** Extract text from PDF resumes

**Key Functions:**
- `extract_text_from_pdf(file)` - Extract text from PDF file object
- `clean_pdf_text(text)` - Clean and normalize extracted text

**Dependencies:**
- PyPDF2 for PDF parsing
- Handles various PDF formats and encodings

**Error Handling:**
- Graceful failure for corrupted PDFs
- Encoding detection and normalization

---

### 📝 Resume Extractor (`resume_extractor.py`)
**Purpose:** Parse and extract structured information from resumes

**Key Functions:**
- `extract_resume_text(pdf_path)` - Extract raw text from resume
- `parse_resume_sections(text)` - Identify resume sections
- `extract_skills(text)` - Extract technical skills
- `extract_education(text)` - Parse education information
- `extract_experience(text)` - Parse work experience

**Preprocessing Integration:**
- Uses `text_preprocessing.py` for text cleaning
- Preserves technical terms and skills

---

### 🧠 Text Preprocessing (`text_preprocessing.py`)
**Purpose:** NLP preprocessing pipeline with stop word removal

**Key Class:** `ResumeTextPreprocessor`

**Features:**
- **177 stop words** removal (vs 23 in basic version)
- Technical term preservation (Python, JavaScript, React, etc.)
- Text normalization and cleaning
- PDF artifact removal
- Email/phone anonymization

**Key Methods:**
- `preprocess_text(text, preserve_structure=True)` - Full preprocessing
- `preprocess_for_matching(text)` - Optimized for matching algorithms
- `_basic_clean(text)` - Remove artifacts and normalize
- `_standardize_technical_terms(text)` - Normalize tech terms
- `_normalize_education_terms(text)` - Standardize degrees

**Stop Word Categories:**
- Articles: a, an, the
- Pronouns: I, me, my, we, our, etc.
- Conjunctions: and, but, or, etc.
- Prepositions: in, on, at, from, etc.
- Common verbs: have, has, is, are, etc.
- Filler words: very, many, also, just, etc.

**Preserved Terms:**
- Programming languages: Python, Java, C++, JavaScript, TypeScript
- Frameworks: React.js, Node.js, Vue.js, Angular, Django, Flask
- Databases: MySQL, PostgreSQL, MongoDB, SQL
- Tools: Git, Docker, AWS, Azure, Kubernetes

**Usage:**
```python
from app.utils.text_preprocessing import preprocess_resume_text

# For display/storage
clean_text = preprocess_resume_text(raw_text, for_matching=False)

# For matching algorithms
match_text = preprocess_resume_text(raw_text, for_matching=True)
```

---

### 🔄 ChromaDB Sync (`chroma_sync.py`)
**Purpose:** Synchronize data between SQLite and ChromaDB vector database

**Key Functions:**
- `sync_resume_to_chroma(user_id)` - Add/update resume in ChromaDB
- `sync_job_to_chroma(job_id)` - Add/update job in ChromaDB
- `sync_all_data()` - Full database synchronization
- `remove_from_chroma(collection, doc_id)` - Remove document

**Collections:**
- `resumes_collection` - User resume embeddings
- `jobs_collection` - Job description embeddings

**When Sync Happens:**
- On resume upload
- On job posting creation
- On job update
- Manual sync via scripts

---

### ⏰ Sync Scheduler (`sync_scheduler.py`)
**Purpose:** Background job scheduler for automatic synchronization

**Features:**
- Periodic ChromaDB synchronization
- Database cleanup tasks
- Embedding refresh
- Error recovery

**Configuration:**
- Sync interval: Configurable (default: hourly)
- Retry logic for failed syncs
- Logging of sync operations

---

## Utility Dependencies

```
Utils Module Dependencies:
├── security.py
│   └── Requires: Flask session, logging
├── decorators.py
│   └── Requires: security.py, Flask
├── pdf_processor.py
│   └── Requires: PyPDF2, io
├── resume_extractor.py
│   └── Requires: pdf_processor.py, text_preprocessing.py
├── text_preprocessing.py
│   └── Requires: re, string
├── chroma_sync.py
│   └── Requires: ChromaDB, matching_service, models
└── sync_scheduler.py
    └── Requires: chroma_sync.py, schedule
```

## Adding New Utilities

To add a new utility module:

1. **Create the module file** in `app/utils/`
2. **Import in `__init__.py`** if needed for app-wide access
3. **Add tests** in `tests/`
4. **Update this README** with documentation

## Best Practices

✅ **DO:**
- Keep utilities stateless when possible
- Use type hints for function parameters
- Handle errors gracefully with try-except
- Log important operations
- Write comprehensive docstrings

❌ **DON'T:**
- Store state in utility modules
- Import app context unnecessarily
- Create circular dependencies
- Hardcode configuration values

## Testing Utilities

```bash
# Test preprocessing
python tests/test_preprocessing_simple.py

# Test on actual resumes
python scripts/test_new_preprocessing.py

# Run all utility tests
python -m pytest tests/ -k "test_"
```
