# Hirely - AI-Powered Job Matching System

Hirely is an intelligent recruitment platform that uses natural language processing and machine learning to match job seekers with relevant opportunities. The system provides multi-admin support, enterprise-level security, and AI-powered candidate ranking.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation
```bash
# Clone the repository
git clone [your-repo-url]
cd Hirely

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database with sample data
python scripts/init_database.py

# Initialize ChromaDB for AI matching
python scripts/init_chroma.py

# Run the application
python run.py
```

Visit: http://localhost:5000

**Default Accounts:**
- Admin: `admin@hirely.dev` / `admin123`
- User: `user@hirely.dev` / `user123`

## 📁 Project Structure

```
Hirely/
├── app/                          # Main Flask application package
│   ├── __init__.py              # App factory and configuration
│   ├── models.py                # Database models (User, Job, Application)
│   ├── routes/                  # Blueprint route modules
│   │   ├── applications.py      # Job application routes
│   │   ├── auth.py             # Authentication API routes
│   │   ├── jobs.py             # Job management API routes
│   │   ├── main.py             # Main web interface routes
│   │   ├── matchmaking.py      # AI matching routes
│   │   └── shortlist.py        # Candidate shortlisting routes
│   ├── static/                 # Static assets (CSS, JS, images)
│   ├── templates/              # Jinja2 HTML templates
│   └── utils/                  # Utility modules
│       ├── decorators.py       # Route decorators
│       ├── pdf_processor.py    # PDF handling utilities
│       ├── resume_extractor.py # Resume text extraction
│       ├── text_preprocessing.py # NLP preprocessing pipeline
│       └── security.py         # Security utilities and decorators
├── chroma_storage/             # ChromaDB vector database storage
├── data/                       # ML models and data files
├── instance/                   # Instance-specific configuration
├── scripts/                    # Development and maintenance scripts
│   ├── migrations/             # Database migration scripts
│   ├── init_database.py        # Database initialization
│   ├── init_chroma.py          # ChromaDB setup
│   ├── create_test_jobs.py     # Test data creation
│   └── [other utilities]       # Various development tools
├── tests/                      # Comprehensive test suite
│   ├── test_cache_prevention.py # Browser security tests
│   ├── test_multi_admin.py      # Admin isolation tests
│   └── test_session_security.py # Session management tests
├── uploads/                    # User uploaded files (resumes, etc.)
├── matching_service.py         # AI matching service core
├── resume_extractor.py         # Resume text extraction utilities
├── run.py                     # Application entry point
└── requirements.txt           # Python dependencies
```

## ✨ Key Features

### 🤖 AI-Powered Matching
- **Vector Embeddings**: Semantic understanding using SentenceTransformers
- **Unified Scoring Algorithm**: Consistent 70% cosine similarity + 30% BM25 across admin shortlisting and user matchmaking
- **Advanced NLP Preprocessing**: Comprehensive text standardization with technical term normalization
- **K-means Clustering**: Intelligent job categorization
- **Real-time Recommendations**: Instant job suggestions based on preprocessed resume content
- **Match Explanations**: Transparent scoring and ranking explanations with detailed analysis

### 👥 Multi-Admin System
- **Complete Isolation**: Each admin operates in their own workspace
- **Ownership Verification**: All job operations verify admin ownership
- **Secure Dashboards**: Admins see only their own job postings
- **Protected Routes**: Edit/delete operations require ownership validation
- **Resume Access Control**: Restricted to applicants of admin's own jobs

### 🔒 Enterprise Security
- **Session Management**: 30-minute timeout with automatic invalidation
- **Browser Cache Prevention**: No back-button access after logout
- **Security Headers**: XSS protection, clickjacking prevention
- **Audit Logging**: Comprehensive security event logging
- **Access Control**: Role-based permissions and route protection

### 📊 User Experience
- **Dual Interfaces**: Separate dashboards for job seekers and employers
- **File Processing**: PDF and DOCX resume support
- **Application Tracking**: Complete application lifecycle management
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Technology Stack

### Backend
- **Framework**: Python Flask with Blueprint architecture
- **Databases**: 
  - SQLite (Main application data)
  - ChromaDB (Vector embeddings storage)
- **Authentication**: Session-based with role management
- **Security**: Custom decorators and middleware

### AI/ML Components
- **SentenceTransformers**: all-MiniLM-L6-v2 for embeddings
- **Natural Language Processing**: Comprehensive text preprocessing with technical term standardization
- **scikit-learn**: K-means clustering for job categorization
- **BM25**: Traditional ranking algorithm for text similarity
- **PyPDF2 & mammoth**: Document text extraction

### Frontend
- **Templates**: Jinja2 HTML templates
- **Styling**: Custom CSS with responsive design
- **JavaScript**: Enhanced user interactions

## � Natural Language Processing

### Text Preprocessing Pipeline
The system includes a comprehensive NLP preprocessing pipeline that standardizes and enhances resume text for better matching accuracy:

#### Key Features
- **Technical Term Standardization**: Normalizes programming languages, frameworks, and tools
- **Education Normalization**: Standardizes degree names and academic qualifications
- **Privacy Protection**: Removes or masks personal information (emails, phone numbers, addresses)
- **Text Cleaning**: Handles whitespace, special characters, and formatting inconsistencies
- **Case Normalization**: Consistent text casing for better matching

#### ResumeTextPreprocessor Class
```python
from app.utils.text_preprocessing import ResumeTextPreprocessor

processor = ResumeTextPreprocessor()
processed_text = processor.preprocess_resume_text(raw_text)
```

#### Processing Steps
1. **Basic Cleaning**: Remove extra whitespace and normalize formatting
2. **Technical Standardization**: Convert variations of tech terms to standard forms
3. **Education Standardization**: Normalize degree and qualification names
4. **Privacy Protection**: Remove sensitive personal information
5. **Final Normalization**: Consistent casing and formatting

### Migration and Data Processing
- **Automatic Processing**: All uploaded resumes are automatically preprocessed
- **Bulk Migration**: Existing resumes can be batch processed using migration scripts
- **ChromaDB Integration**: Preprocessed text is stored in vector database for similarity matching

## 🎯 Unified Scoring Algorithm

### Scoring Formula
The system uses a consistent scoring algorithm across both admin shortlisting and user matchmaking:

**Final Score = (Cosine Similarity × 70%) + (BM25 Score × 30%)**

#### Components
- **Cosine Similarity (70%)**: Semantic understanding through vector embeddings
- **BM25 Score (30%)**: Traditional keyword-based ranking
- **Preprocessing**: Both components use standardized, preprocessed text

#### Implementation
- **Admin Shortlisting**: Ranks candidates for job postings
- **User Matchmaking**: Recommends jobs to users based on their resume
- **Detailed Explanations**: Provides breakdown of scoring components

### Benefits
- **Consistency**: Same algorithm ensures fair comparison across interfaces
- **Transparency**: Users and admins see the same scoring logic
- **Accuracy**: Combination of semantic and keyword matching improves relevance

## �🧪 Testing

### Automated Tests
```bash
# Security tests
python tests/test_session_security.py
python tests/test_cache_prevention.py
python tests/test_multi_admin.py
```

### Test Coverage
- **Security Testing**: Session management, cache prevention, multi-admin isolation
- **Integration Testing**: Database connections, AI matching functionality
- **API Testing**: All routes and authentication flows

## 🔧 Development

### Database Management
```bash
# Create fresh database
python scripts/init_database.py

# Reset database (WARNING: Deletes all data)
python scripts/init_database.py --reset

# Run migrations
python scripts/migrations/migrate_add_created_by.py
```

### ChromaDB Management
```bash
# Initialize ChromaDB
python scripts/init_chroma.py

# Reset ChromaDB
python scripts/reset_chroma.py

# Import bulk data
python scripts/import_data_to_chroma.py
```

### Create Test Data
```bash
# Create sample job postings
python scripts/create_test_jobs.py

# Bulk add resumes to ChromaDB with preprocessing
python scripts/bulk_add_resumes_to_chroma.py

# Extract and preprocess existing resume texts
python scripts/extract_existing_resume_texts.py
```

### Environment Verification
```bash
# Check setup
python scripts/check_env.py

# Test AI matching
python scripts/test_matching.py
```

## 📚 API Documentation

### Authentication Routes (`/api/auth`)
- `POST /api/auth/login` - User authentication
- `POST /api/auth/logout` - Session termination
- `POST /api/auth/register` - User registration

### Job Management (`/api/jobs`)
- `GET /api/jobs/` - List jobs
- `POST /api/jobs/` - Create job (admin only)
- `DELETE /api/jobs/<id>` - Delete job (admin only)

### Matching & Applications
- `POST /api/matchmaking/match` - Get job matches for user
- `GET /api/matchmaking/explain/<id>` - Get detailed match explanation and scoring breakdown
- `POST /api/applications/apply` - Apply to job
- `GET /api/shortlist/<id>` - Get shortlisted candidates with unified scoring

## 🏗️ Database Architecture

### Core Models
- **User**: Authentication and profile management
- **Job**: Job postings with admin ownership
- **Application**: User job applications with status tracking

### Relationships
- Users → Applications (One-to-Many)
- Jobs → Applications (One-to-Many)
- Users (Admin) → Jobs (One-to-Many via created_by)

### ChromaDB Collections
- **Resumes**: Vector embeddings of preprocessed resume content with NLP standardization
- **Jobs**: Vector embeddings of job descriptions

## 🔐 Security Features

### Session Security
- **Timeout Management**: 30-minute automatic logout
- **Activity Tracking**: Last activity timestamp updates
- **Invalid Session Handling**: Graceful cleanup of corrupted sessions
- **Security Audit**: Comprehensive event logging

### Browser Security
- **Cache Prevention**: No-cache headers on protected routes
- **Back-Button Protection**: Prevents cached content access after logout
- **Security Headers**: X-Frame-Options, X-XSS-Protection, X-Content-Type-Options
- **Cookie Security**: HTTPOnly and Secure flags

### Access Control
- **Role-Based Permissions**: Admin vs. user access levels
- **Ownership Verification**: Admins can only modify their own content
- **Route Protection**: Security decorators on all sensitive endpoints
- **CSRF Protection**: Session-based security measures

## 🤝 Team Collaboration

### Database Sharing
- **Current Setup**: Database and ChromaDB content shared via git
- **Collaboration**: All team members get the same data when pulling
- **Conflict Resolution**: Communication recommended for database changes

### Development Workflow
1. **Setup**: Each developer runs initialization scripts
2. **Features**: Create feature branches for new functionality
3. **Testing**: Run full test suite before committing
4. **Database Changes**: Use migration scripts for schema changes

### Best Practices
- **Code Review**: All changes should be reviewed
- **Testing**: Maintain test coverage for new features
- **Security**: Use provided decorators for route protection
- **Documentation**: Update README for significant changes

## 🚨 Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Reset database
python scripts/init_database.py --reset
```

**ChromaDB Issues:**
```bash
# Clear and reinitialize ChromaDB
python scripts/reset_chroma.py
python scripts/init_chroma.py
```

**Import Errors:**
```bash
# Verify dependencies
pip install -r requirements.txt

# Check environment
python scripts/check_env.py
```

**Session/Login Issues:**
- Clear browser cache and cookies
- Check if database has user accounts
- Verify session timeout settings

### Performance Optimization
- **Database**: Use indexes for frequent queries
- **ChromaDB**: Batch operations for large datasets
- **Caching**: Browser caching for static assets
- **Monitoring**: Check logs for performance bottlenecks

## 📈 Future Enhancements

### Planned Features
- [ ] Email notifications for applications
- [ ] Advanced search and filtering
- [ ] Resume builder integration
- [ ] Interview scheduling
- [ ] Analytics dashboard
- [ ] Mobile application

### Technical Improvements
- [ ] PostgreSQL migration for production
- [ ] Redis caching layer
- [ ] API rate limiting
- [ ] Containerization with Docker
- [ ] CI/CD pipeline
- [ ] Performance monitoring

## 📄 License

This project is proprietary and confidential. All rights reserved.

## 🆘 Support

For technical support or questions:
1. Check this README for common solutions
2. Review the test suite for usage examples
3. Examine the code documentation
4. Contact the development team

---

**Version**: 2.1.0 (Enhanced NLP and Unified Scoring Release)
**Last Updated**: October 2025
**Maintainers**: Development Team