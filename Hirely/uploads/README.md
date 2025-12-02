# Uploads Directory

This directory stores user-uploaded resume files (PDFs).

## Overview

When users upload their resumes through the profile page, PDF files are saved here with secure, timestamped filenames.

## File Naming Convention

```
[Original_Filename]_[Unix_Timestamp].pdf
```

**Examples:**
- `John_Doe_Resume_1759660898.pdf`
- `Maria_Cruz_Resume_1764683176.pdf`
- `Angela_Torres_Resume_1759669257.pdf`

**Benefits:**
- ✅ Prevents filename collisions
- ✅ Maintains original name for context
- ✅ Chronological ordering by timestamp
- ✅ Unique identifier for database reference

## Directory Structure

```
uploads/
├── John_Doe_Resume_1759660898.pdf
├── Maria_Cruz_Resume_1764683176.pdf
├── Angela_Torres_Resume_1759669257.pdf
└── [more resume files...]
```

## File Processing Pipeline

```
User Uploads Resume
        ↓
1. Validate file type (PDF only)
2. Check file size (max 16MB)
3. Generate secure filename
        ↓
4. Save to uploads/ folder
5. Extract text using PyPDF2
6. Preprocess text (stop word removal)
        ↓
7. Save filename to database (users.resume)
8. Save processed text (applications.resume_text)
9. Create vector embedding (ChromaDB)
        ↓
Available for Job Matching
```

## Security

### File Type Validation
```python
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

### File Size Limit
```python
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
```

### Secure Filename Generation
```python
import time
from werkzeug.utils import secure_filename

original_name = secure_filename(file.filename)
timestamp = int(time.time())
filename = f"{original_name}_{timestamp}.pdf"
```

### Access Control
- ❌ **Users:** Cannot view other users' resumes
- ✅ **Admins:** Can view resumes of applicants to their jobs only
- ✅ **File Serving:** Through Flask route with auth check

## Storage Capacity

Current setup:
- **Max File Size:** 16 MB per resume
- **100 resumes:** ~500 MB (avg 5 MB each)
- **1000 resumes:** ~5 GB (avg 5 MB each)

## Backup Strategy

### Manual Backup
```bash
# Create timestamped backup
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

### Automated Backup (Recommended for Production)
```bash
# Add to crontab for daily backups
0 2 * * * tar -czf /backups/uploads_$(date +\%Y\%m\%d).tar.gz /path/to/uploads/
```

## File Access

### View Resume (Admin Only)
```python
@app.route('/view_resume/<int:user_id>')
@secure_route
def view_resume(user_id):
    # 1. Check admin permissions
    # 2. Verify user applied to admin's job
    # 3. Serve file
    return send_file(resume_path, mimetype='application/pdf')
```

### Download Resume
```python
return send_file(
    resume_path,
    mimetype='application/pdf',
    as_attachment=True,
    download_name=f"{user.full_name}_Resume.pdf"
)
```

## Maintenance

### Check Storage Usage
```bash
# Get total size
du -sh uploads/

# Count files
ls uploads/ | wc -l

# List largest files
du -h uploads/* | sort -rh | head -10
```

### Clean Old Files (Optional)
```bash
# Find files older than 1 year
find uploads/ -name "*.pdf" -mtime +365

# Delete (be careful!)
find uploads/ -name "*.pdf" -mtime +365 -delete
```

### Verify File Integrity
```bash
# Check for corrupted PDFs
for file in uploads/*.pdf; do
    pdfinfo "$file" > /dev/null 2>&1 || echo "Corrupted: $file"
done
```

## .gitignore Configuration

### Option 1: Share Upload Files (Current Setup)
```gitignore
# Uploads are committed to repository
# Good for: Development, small teams, test data
```

### Option 2: Keep Uploads Local
```gitignore
# Add to .gitignore
uploads/*
!uploads/.gitkeep
```

### Option 3: Exclude Specific File Types
```gitignore
# Keep folder structure, exclude PDFs
uploads/*.pdf
uploads/*.docx
```

## Error Handling

### File Upload Errors

**Issue:** "File too large"
```python
# Solution: Increase MAX_CONTENT_LENGTH
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB
```

**Issue:** "Permission denied"
```bash
# Solution: Fix folder permissions
chmod 755 uploads/
```

**Issue:** "Disk full"
```bash
# Solution: Clean up old files or increase storage
df -h  # Check disk usage
```

## Production Considerations

### Cloud Storage (Recommended for Production)

Instead of local storage, use:
- **AWS S3**
- **Google Cloud Storage**
- **Azure Blob Storage**

**Benefits:**
- ✅ Unlimited scalability
- ✅ Automatic backups
- ✅ CDN integration
- ✅ Better security
- ✅ Cost-effective for large scale

### Example: AWS S3 Integration
```python
import boto3

s3 = boto3.client('s3')
s3.upload_file(
    local_file,
    'hirely-resumes',
    f'resumes/{filename}'
)
```

## Privacy & GDPR Compliance

⚠️ **Important Considerations:**
- Resumes contain **Personally Identifiable Information (PII)**
- Implement **data retention policies**
- Provide **user data deletion** on request
- Secure storage with **encryption at rest**
- Log **file access** for audit trails

### Data Deletion
```python
@app.route('/delete_account', methods=['POST'])
@secure_route
def delete_account():
    # 1. Delete resume file
    if user.resume:
        os.remove(os.path.join('uploads', user.resume))
    
    # 2. Delete from database
    db.session.delete(user)
    db.session.commit()
```

## Related Files

- `app/routes/main.py` - Resume upload route (`/update_profile`)
- `app/utils/pdf_processor.py` - PDF text extraction
- `app/utils/resume_extractor.py` - Resume parsing
- `app/models.py` - User model with resume field
- `instance/config.py` - Upload folder configuration
