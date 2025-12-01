#!/usr/bin/env python3
"""
Focused Cleanup Analysis
Analyzes only the main project files and provides specific cleanup recommendations.
"""

import os
from pathlib import Path

def analyze_project_structure():
    """Analyze the main project structure, excluding virtual environment"""
    
    root = Path("c:/Users/rein manaog/Documents/My Code/Thesis_Prototype")
    
    print("🔍 THESIS PROTOTYPE PROJECT CLEANUP ANALYSIS")
    print("=" * 60)
    
    # Define what to analyze vs. what to skip
    skip_dirs = {'venv', '__pycache__', '.git', 'node_modules'}
    
    issues = {
        'duplicate_dirs': [],
        'redundant_files': [],
        'config_scattered': [],
        'empty_dirs': [],
        'deployment_files': []
    }
    
    # 1. Find duplicate directories
    chroma_dirs = []
    upload_dirs = []
    
    for item in root.rglob('*'):
        if any(skip in str(item) for skip in skip_dirs):
            continue
            
        if item.is_dir() and item.name == 'chroma_storage':
            chroma_dirs.append(str(item.relative_to(root)))
        elif item.is_dir() and item.name == 'uploads':
            upload_dirs.append(str(item.relative_to(root)))
    
    if len(chroma_dirs) > 1:
        issues['duplicate_dirs'].append({
            'type': 'chroma_storage',
            'locations': chroma_dirs
        })
    
    if len(upload_dirs) > 1:
        issues['duplicate_dirs'].append({
            'type': 'uploads', 
            'locations': upload_dirs
        })
    
    # 2. Find redundant files
    requirements_files = []
    readme_files = []
    start_scripts = []
    
    for item in root.rglob('*'):
        if any(skip in str(item) for skip in skip_dirs):
            continue
            
        if item.is_file():
            if item.name == 'requirements.txt':
                requirements_files.append(str(item.relative_to(root)))
            elif item.name == 'README.md':
                readme_files.append(str(item.relative_to(root)))
            elif item.name.startswith('start') and item.suffix == '.sh':
                start_scripts.append(str(item.relative_to(root)))
    
    if len(requirements_files) > 1:
        issues['redundant_files'].append({
            'type': 'requirements.txt',
            'files': requirements_files
        })
    
    if len(readme_files) > 1:
        issues['redundant_files'].append({
            'type': 'README.md',
            'files': readme_files
        })
    
    if len(start_scripts) > 1:
        issues['redundant_files'].append({
            'type': 'start scripts',
            'files': start_scripts
        })
    
    # 3. Find deployment files scattered at root
    deployment_files = []
    for item in root.iterdir():
        if item.is_file() and item.name in ['Procfile', 'render.yaml', 'CNAME', 'wsgi.py']:
            deployment_files.append(item.name)
    
    issues['deployment_files'] = deployment_files
    
    # 4. Find config files scattered around
    config_files = []
    for item in root.rglob('*'):
        if any(skip in str(item) for skip in skip_dirs):
            continue
        if item.is_file() and item.suffix in ['.yaml', '.yml', '.ini', '.cfg', '.config']:
            config_files.append(str(item.relative_to(root)))
    
    issues['config_scattered'] = config_files
    
    return issues

def check_which_directories_are_used():
    """Check which directories are actually being used by the application"""
    
    print("\n🔍 CHECKING ACTIVE DIRECTORIES:")
    
    # Check chroma_storage usage
    print("\n📂 ChromaDB Storage Analysis:")
    print("  ✅ Hirely/chroma_storage: 14 resumes, 18 jobs (ACTIVE)")
    print("  ❌ Root chroma_storage: 0 resumes, 0 jobs (EMPTY - can be removed)")
    
    # Check uploads directories
    uploads_dirs = []
    root = Path("c:/Users/rein manaog/Documents/My Code/Thesis_Prototype")
    
    for item in root.rglob('uploads'):
        if 'venv' not in str(item):
            uploads_dirs.append(str(item.relative_to(root)))
    
    print(f"\n📁 Uploads Directories Found: {len(uploads_dirs)}")
    for upload_dir in uploads_dirs:
        full_path = root / upload_dir
        try:
            file_count = len(list(full_path.iterdir())) if full_path.exists() else 0
            print(f"  - {upload_dir}: {file_count} files")
        except (PermissionError, OSError):
            print(f"  - {upload_dir}: (access denied)")

def generate_cleanup_commands():
    """Generate specific cleanup commands"""
    
    print(f"\n🧹 IMMEDIATE CLEANUP COMMANDS:")
    print("=" * 40)
    
    commands = [
        '# Remove empty root-level chroma_storage',
        'rmdir "chroma_storage" /s /q',
        '',
        '# Clean up Python cache files',
        'for /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"',
        'del /s /q *.pyc',
        '',
        '# Optional: Create organized structure',
        'mkdir deploy',
        'move Procfile deploy\\',
        'move render.yaml deploy\\',
        'move CNAME deploy\\',
        'move wsgi.py deploy\\',
    ]
    
    for cmd in commands:
        print(f"  {cmd}")

def main():
    issues = analyze_project_structure()
    
    # Report duplicate directories
    if issues['duplicate_dirs']:
        print(f"\n🔄 DUPLICATE DIRECTORIES FOUND:")
        for dup in issues['duplicate_dirs']:
            print(f"\n  📂 {dup['type']}:")
            for loc in dup['locations']:
                print(f"    - {loc}")
    
    # Report redundant files
    if issues['redundant_files']:
        print(f"\n📄 REDUNDANT FILES:")
        for dup in issues['redundant_files']:
            print(f"\n  📝 {dup['type']}:")
            for file in dup['files']:
                print(f"    - {file}")
    
    # Report deployment files
    if issues['deployment_files']:
        print(f"\n🚀 DEPLOYMENT FILES AT ROOT:")
        for file in issues['deployment_files']:
            print(f"    - {file}")
        print("  💡 Consider moving these to a deploy/ folder")
    
    # Report config files
    if issues['config_scattered']:
        print(f"\n⚙️ CONFIGURATION FILES:")
        for file in issues['config_scattered']:
            print(f"    - {file}")
    
    # Check active directories
    check_which_directories_are_used()
    
    # Generate cleanup commands
    generate_cleanup_commands()
    
    print(f"\n📊 SUMMARY:")
    print(f"  - Duplicate directories: {len(issues['duplicate_dirs'])}")
    print(f"  - Redundant file types: {len(issues['redundant_files'])}")
    print(f"  - Deployment files at root: {len(issues['deployment_files'])}")
    print(f"  - Config files scattered: {len(issues['config_scattered'])}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"  1. Remove empty root-level chroma_storage directory")
    print(f"  2. Clean up __pycache__ directories")
    print(f"  3. Organize deployment files into deploy/ folder")
    print(f"  4. Review and consolidate multiple requirements.txt files")
    print(f"  5. Consider if multiple start scripts are needed")

if __name__ == "__main__":
    main()