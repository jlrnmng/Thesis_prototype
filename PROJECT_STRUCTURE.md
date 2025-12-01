# Thesis Prototype Project Structure

## Directory Usage Summary

### Active Directories:
- ✅ **Hirely/chroma_storage**: ChromaDB vector database (14 resumes, 18 jobs)
- ✅ **Hirely/uploads**: Main file upload directory (17 files)
- ✅ **Hirely/app/uploads**: Secondary upload directory (2 files)

### Configuration Files:
- **requirements.txt**: Root-level dependencies for deployment
- **Hirely/requirements.txt**: Application-specific dependencies
- **deploy/**: Deployment configuration files (Procfile, render.yaml, etc.)

### Scripts and Tools:
- **scripts/**: Database management and analysis tools
- **Hirely/scripts/**: Application-specific utility scripts

### Development:
- **k-means_model_training/**: Machine learning model development
- **Hirely/tests/**: Unit tests
- **Hirely/venv/**: Python virtual environment

## Cleanup Actions Performed:
1. ✅ Removed empty root-level chroma_storage directory
2. ✅ Cleaned up __pycache__ directories
3. ✅ Organized deployment files into deploy/ folder
4. ✅ Removed empty upload directories

## Next Steps:
- Review if both requirements.txt files are needed
- Consider consolidating start scripts
- Review README files for redundancy
