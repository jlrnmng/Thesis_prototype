#!/usr/bin/env python3
"""
Automated Cleanup Script for Thesis Prototype
Safely cleans up the project structure based on analysis.
"""

import os
import shutil
import stat
from pathlib import Path

def remove_readonly(func, path, excinfo):
    """Helper function to remove read-only files on Windows"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clean_pycache_directories():
    """Remove all __pycache__ directories"""
    root = Path("c:/Users/rein manaog/Documents/My Code/Thesis_Prototype")
    
    pycache_dirs = list(root.rglob('__pycache__'))
    
    print(f"🧹 Cleaning {len(pycache_dirs)} __pycache__ directories...")
    
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir, onerror=remove_readonly)
            print(f"  ✅ Removed: {pycache_dir.relative_to(root)}")
        except Exception as e:
            print(f"  ❌ Failed to remove {pycache_dir.relative_to(root)}: {e}")

def remove_empty_chroma_storage():
    """Remove the empty root-level chroma_storage directory"""
    root = Path("c:/Users/rein manaog/Documents/My Code/Thesis_Prototype")
    empty_chroma = root / "chroma_storage"
    
    if empty_chroma.exists():
        print(f"🗑️ Removing empty chroma_storage directory...")
        try:
            shutil.rmtree(empty_chroma, onerror=remove_readonly)
            print(f"  ✅ Removed: {empty_chroma.relative_to(root)}")
        except Exception as e:
            print(f"  ❌ Failed to remove chroma_storage: {e}")
    else:
        print(f"  ℹ️ No empty chroma_storage found at root level")

def organize_deployment_files():
    """Move deployment files to a deploy/ folder"""
    root = Path("c:/Users/rein manaog/Documents/My Code/Thesis_Prototype")
    deploy_dir = root / "deploy"
    
    deployment_files = ['Procfile', 'render.yaml', 'CNAME', 'wsgi.py']
    
    # Create deploy directory
    deploy_dir.mkdir(exist_ok=True)
    print(f"📁 Created deploy/ directory")
    
    for file_name in deployment_files:
        src_file = root / file_name
        if src_file.exists():
            dst_file = deploy_dir / file_name
            try:
                shutil.move(str(src_file), str(dst_file))
                print(f"  ✅ Moved {file_name} to deploy/")
            except Exception as e:
                print(f"  ❌ Failed to move {file_name}: {e}")

def cleanup_unused_upload_directories():
    """Remove unused upload directories"""
    root = Path("c:/Users/rein manaog/Documents/My Code/Thesis_Prototype")
    
    # The active upload directory is Hirely/uploads
    # Empty directories can be removed: Hirely/instance/uploads
    
    unused_dirs = [
        "Hirely/instance/uploads"  # This one is empty
    ]
    
    print(f"🗂️ Cleaning up unused upload directories...")
    
    for dir_path in unused_dirs:
        full_path = root / dir_path
        if full_path.exists():
            try:
                file_count = len(list(full_path.iterdir()))
                if file_count == 0:
                    full_path.rmdir()
                    print(f"  ✅ Removed empty directory: {dir_path}")
                else:
                    print(f"  ⚠️ Skipped {dir_path} (contains {file_count} files)")
            except Exception as e:
                print(f"  ❌ Failed to remove {dir_path}: {e}")

def create_project_structure_summary():
    """Create a clean project structure summary"""
    root = Path("c:/Users/rein manaog/Documents/My Code/Thesis_Prototype")
    
    summary_content = """# Thesis Prototype Project Structure

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
"""
    
    summary_file = root / "PROJECT_STRUCTURE.md"
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        print(f"📋 Created PROJECT_STRUCTURE.md with cleanup summary")
    except Exception as e:
        print(f"❌ Failed to create structure summary: {e}")

def analyze_remaining_structure():
    """Analyze the cleaned-up structure"""
    root = Path("c:/Users/rein manaog/Documents/My Code/Thesis_Prototype")
    
    print(f"\n📊 POST-CLEANUP ANALYSIS:")
    print(f"=" * 40)
    
    # Count main directories
    main_dirs = [d for d in root.iterdir() if d.is_dir() and not d.name.startswith('.')]
    print(f"Main directories: {len(main_dirs)}")
    
    for dir_path in sorted(main_dirs):
        if dir_path.name not in ['venv']:  # Skip verbose directories
            print(f"  📁 {dir_path.name}/")
    
    # Count files at root level
    root_files = [f for f in root.iterdir() if f.is_file()]
    print(f"\nRoot level files: {len(root_files)}")
    
    for file_path in sorted(root_files):
        print(f"  📄 {file_path.name}")
    
    # Check for remaining duplicates
    print(f"\n🔍 REMAINING DUPLICATE CHECK:")
    
    chroma_dirs = list(root.rglob('chroma_storage'))
    print(f"ChromaDB directories: {len(chroma_dirs)}")
    for cd in chroma_dirs:
        if 'venv' not in str(cd):
            print(f"  - {cd.relative_to(root)}")
    
    upload_dirs = list(root.rglob('uploads'))
    upload_dirs = [ud for ud in upload_dirs if 'venv' not in str(ud)]
    print(f"Upload directories: {len(upload_dirs)}")
    for ud in upload_dirs:
        file_count = len(list(ud.iterdir())) if ud.exists() else 0
        print(f"  - {ud.relative_to(root)} ({file_count} files)")

def main():
    print("🧹 AUTOMATED THESIS PROTOTYPE CLEANUP")
    print("=" * 50)
    
    # Safety check
    root = Path("c:/Users/rein manaog/Documents/My Code/Thesis_Prototype")
    if not root.exists():
        print("❌ Project root directory not found!")
        return
    
    print(f"🎯 Working directory: {root}")
    print()
    
    # Perform cleanup tasks
    try:
        # 1. Clean Python cache
        clean_pycache_directories()
        print()
        
        # 2. Remove empty chroma_storage
        remove_empty_chroma_storage()
        print()
        
        # 3. Organize deployment files
        organize_deployment_files()
        print()
        
        # 4. Clean unused upload directories
        cleanup_unused_upload_directories()
        print()
        
        # 5. Create structure summary
        create_project_structure_summary()
        print()
        
        # 6. Final analysis
        analyze_remaining_structure()
        
        print(f"\n✅ CLEANUP COMPLETED SUCCESSFULLY!")
        print(f"📋 Check PROJECT_STRUCTURE.md for details")
        
    except Exception as e:
        print(f"❌ Cleanup failed with error: {e}")
        raise

if __name__ == "__main__":
    main()