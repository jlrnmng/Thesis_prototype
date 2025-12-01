#!/usr/bin/env python3
"""
Folder Structure Analysis and Cleanup Recommendations
Analyzes the Thesis_Prototype directory structure and provides cleanup recommendations.
"""

import os
import json
from pathlib import Path
from collections import defaultdict

def analyze_directory(root_path):
    """Analyze directory structure and identify issues"""
    
    root = Path(root_path)
    analysis = {
        'duplicates': [],
        'empty_dirs': [],
        'large_files': [],
        'config_files': [],
        'cache_dirs': [],
        'redundant_files': [],
        'size_analysis': {},
        'structure': {}
    }
    
    # Track file sizes and duplicates
    file_hashes = defaultdict(list)
    
    def get_dir_structure(path, level=0, max_level=3):
        """Get directory structure with size info"""
        if level > max_level:
            return "..."
        
        items = {}
        try:
            for item in path.iterdir():
                if item.is_dir():
                    items[f"{item.name}/"] = get_dir_structure(item, level+1, max_level)
                else:
                    size = item.stat().st_size
                    size_str = format_size(size)
                    items[item.name] = f"{size_str}"
                    
                    # Track large files
                    if size > 10 * 1024 * 1024:  # > 10MB
                        analysis['large_files'].append({
                            'path': str(item.relative_to(root)),
                            'size': size,
                            'size_str': size_str
                        })
        except PermissionError:
            return "Permission Denied"
        
        return items
    
    def format_size(size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
    
    # Get full structure
    analysis['structure'] = get_dir_structure(root)
    
    # Analyze specific patterns
    for item in root.rglob('*'):
        rel_path = item.relative_to(root)
        
        if item.is_dir():
            # Check for empty directories
            try:
                if not any(item.iterdir()):
                    analysis['empty_dirs'].append(str(rel_path))
            except (PermissionError, OSError):
                pass
            
            # Check for cache/temp directories
            if any(name in item.name.lower() for name in ['__pycache__', 'cache', 'temp', '.git']):
                analysis['cache_dirs'].append(str(rel_path))
        
        elif item.is_file():
            # Check for config files
            if item.suffix in ['.json', '.yaml', '.yml', '.ini', '.cfg', '.config']:
                analysis['config_files'].append(str(rel_path))
            
            # Check for potential duplicates by name
            filename = item.name
            if filename in ['requirements.txt', 'README.md', 'start.sh', '__init__.py']:
                analysis['redundant_files'].append(str(rel_path))
    
    return analysis

def find_duplicate_directories():
    """Find directories with similar names that might be duplicates"""
    root = Path("c:/Users/rein manaog/Documents/My Code/Thesis_Prototype")
    
    duplicates = []
    
    # Check for chroma_storage duplicates
    chroma_dirs = list(root.rglob('chroma_storage'))
    if len(chroma_dirs) > 1:
        duplicates.append({
            'type': 'chroma_storage',
            'locations': [str(d.relative_to(root)) for d in chroma_dirs],
            'recommendation': 'Keep Hirely/chroma_storage (has data), remove root-level one (empty)'
        })
    
    # Check for uploads directories
    upload_dirs = list(root.rglob('uploads'))
    if len(upload_dirs) > 1:
        duplicates.append({
            'type': 'uploads',
            'locations': [str(d.relative_to(root)) for d in upload_dirs],
            'recommendation': 'Check which uploads directory is being used by the app'
        })
    
    return duplicates

def generate_cleanup_plan():
    """Generate specific cleanup recommendations"""
    
    cleanup_plan = {
        'immediate_actions': [
            "Remove empty root-level chroma_storage directory",
            "Clean up __pycache__ directories",
            "Remove any .pyc files",
            "Check for unused requirements.txt files"
        ],
        'investigation_needed': [
            "Determine which uploads directory is active",
            "Review multiple start.sh scripts",
            "Check if all README.md files are needed",
            "Verify instance/ directory usage"
        ],
        'structure_improvements': [
            "Move all scripts to scripts/ directory",
            "Consolidate configuration files",
            "Create clear separation between app code and deployment files",
            "Consider moving deployment files (Procfile, render.yaml) to a deploy/ folder"
        ]
    }
    
    return cleanup_plan

def main():
    root_path = "c:/Users/rein manaog/Documents/My Code/Thesis_Prototype"
    
    print("🔍 THESIS PROTOTYPE FOLDER STRUCTURE ANALYSIS")
    print("=" * 60)
    
    # Analyze directory structure
    analysis = analyze_directory(root_path)
    
    print("\n📁 DIRECTORY STRUCTURE:")
    print(json.dumps(analysis['structure'], indent=2))
    
    # Find duplicates
    duplicates = find_duplicate_directories()
    
    print(f"\n🔄 DUPLICATE DIRECTORIES FOUND: {len(duplicates)}")
    for dup in duplicates:
        print(f"\n  📂 {dup['type']}:")
        for loc in dup['locations']:
            print(f"    - {loc}")
        print(f"    💡 {dup['recommendation']}")
    
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"  - Empty directories: {len(analysis['empty_dirs'])}")
    print(f"  - Cache directories: {len(analysis['cache_dirs'])}")
    print(f"  - Large files (>10MB): {len(analysis['large_files'])}")
    print(f"  - Config files: {len(analysis['config_files'])}")
    print(f"  - Redundant files: {len(analysis['redundant_files'])}")
    
    if analysis['empty_dirs']:
        print(f"\n📂 Empty directories:")
        for dir_path in analysis['empty_dirs']:
            print(f"    - {dir_path}")
    
    if analysis['cache_dirs']:
        print(f"\n🗂️ Cache directories:")
        for dir_path in analysis['cache_dirs']:
            print(f"    - {dir_path}")
    
    if analysis['large_files']:
        print(f"\n📦 Large files:")
        for file_info in analysis['large_files']:
            print(f"    - {file_info['path']} ({file_info['size_str']})")
    
    if analysis['redundant_files']:
        print(f"\n📄 Potentially redundant files:")
        for file_path in analysis['redundant_files']:
            print(f"    - {file_path}")
    
    # Generate cleanup plan
    cleanup_plan = generate_cleanup_plan()
    
    print(f"\n🧹 CLEANUP PLAN:")
    print(f"\n  ⚡ Immediate Actions:")
    for action in cleanup_plan['immediate_actions']:
        print(f"    - {action}")
    
    print(f"\n  🔍 Investigation Needed:")
    for item in cleanup_plan['investigation_needed']:
        print(f"    - {item}")
    
    print(f"\n  🏗️ Structure Improvements:")
    for improvement in cleanup_plan['structure_improvements']:
        print(f"    - {improvement}")
    
    print(f"\n" + "=" * 60)
    print("Analysis complete! Review the recommendations above.")

if __name__ == "__main__":
    main()