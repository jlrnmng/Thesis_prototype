# App Directory

This directory contains the core Flask application code.

## Directory Structure

```
app/
├── __init__.py           # Flask app factory and configuration
├── models.py             # SQLAlchemy database models
├── routes/               # Application routes (blueprints)
│   ├── __init__.py
│   ├── main.py          # Main routes (home, login, register)
│   ├── auth.py          # Authentication routes
│   ├── jobs.py          # Job posting routes
│   ├── applications.py  # Job application routes
│   ├── matchmaking.py   # Matching algorithm routes
│   └── shortlist.py     # Shortlist management routes
├── static/              # Static files (CSS, JS, images)
│   ├── Hirely_logo.png
│   └── ...
├── templates/           # Jinja2 HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard_user.html
│   ├── dashboard_admin.html
│   ├── profile.html
│   ├── post_job.html
│   └── ...
├── uploads/             # User uploaded files (resumes)
└── utils/               # Utility modules
    ├── chroma_sync.py           # ChromaDB synchronization
    ├── decorators.py            # Custom decorators (@secure_route)
    ├── pdf_processor.py         # PDF text extraction
    ├── resume_extractor.py      # Resume parsing utilities
    ├── security.py              # Security functions
    ├── sync_scheduler.py        # Background sync scheduler
    └── text_preprocessing.py    # Text preprocessing & stop words
```

## Key Components

### Models (`models.py`)
- `User` - User accounts (both job seekers and admins)
- `Job` - Job postings created by admins
- `Application` - Job applications submitted by users

### Routes
- **main.py**: Home, login, register, profile, dashboards
- **jobs.py**: Create, edit, delete job postings
- **applications.py**: Submit and manage applications
- **matchmaking.py**: AI-powered job-resume matching

### Utils
- **text_preprocessing.py**: Stop word removal, text normalization (177 stop words)
- **pdf_processor.py**: Extract text from PDF resumes
- **security.py**: Session security, CSRF protection, secure routes
- **chroma_sync.py**: Sync data with ChromaDB vector database

### Templates
- User dashboard: Job recommendations with match scores
- Admin dashboard: Job management and applicant viewing
- Profile page: Resume upload and user information
- Job posting: Create and edit job descriptions

## Features

### For Job Seekers
✅ Upload PDF resume
✅ Get AI-powered job recommendations
✅ View match scores (BM25 + Cosine Similarity)
✅ Apply to jobs with one click
✅ Update profile and resume

### For Admins/Employers
✅ Post job openings
✅ View applicants with match scores
✅ Download applicant resumes
✅ Edit/delete job postings
✅ Company information display
✅ Multi-admin support (each admin sees only their jobs)

## Configuration

Configuration is loaded from `instance/config.py`:
- Database URI
- Upload folder location
- Session security settings
- ChromaDB settings
