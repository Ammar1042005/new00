#!/usr/bin/env python3
"""
Simple Git commit script for New00 project
"""

import os
import subprocess

def run_git_command(command):
    """Run Git command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"Command executed: {command}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

def commit_changes():
    """Commit all changes"""
    print("Starting Git commit process...")
    
    # Check if Git repository exists
    if not os.path.exists(".git"):
        print("Initializing Git repository...")
        run_git_command("git init")
        
        # Configure Git user
        run_git_command('git config user.name "Shaikh Mohammad Ammar"')
        run_git_command('git config user.email "86150394+Ammar1042005@users.noreply.github.com"')
    
    # Add all files
    print("Adding all files to staging...")
    run_git_command("git add .")
    
    # Create commit message
    commit_message = """feat: Complete modular restructuring with separate feature files

Major Changes:
- Created separate files for each PDF processing tool
- Created separate files for each image processing tool  
- Added comprehensive configuration management (project_config.py)
- Added shared utilities and helpers (utils.py)
- Created complete documentation and sharing guides
- Implemented modular architecture for maximum maintainability

New Files Added:
Core Configuration:
- project_config.py - Comprehensive settings management
- utils.py - Shared utilities and helper classes

PDF Processing Tools:
- pdf_merge.py - Combine multiple PDFs
- pdf_split.py - Split PDF into pages/ranges
- pdf_rotate.py - Rotate PDF pages by angles
- pdf_watermark.py - Add watermarks to PDFs
- pdf_compress.py - Reduce PDF file size

Documentation:
- FEATURES.md - Complete feature overview
- FEATURE_INDEX.md - Detailed file index
- PROJECT_SHARING.md - Complete project sharing guide
- setup_complete_project.bat - Interactive project setup

Benefits:
- Maximum modularity - Each feature in separate file
- Enhanced collaboration - Parallel development support
- Superior scalability - Easy to add new features
- Better testing - Individual feature unit tests
- Professional structure - Industry-standard organization

Ready for enterprise-level development and team collaboration."""
    
    # Create commit
    print("Creating commit...")
    success = run_git_command(f'git commit -m "{commit_message}"')
    
    if success:
        print("Commit successful!")
        
        # Show next steps
        print("\nNext steps:")
        print("1. Create GitHub repository at: https://github.com/new")
        print("2. Add remote: git remote add origin https://github.com/Shaikh-Mohammad-Ammar/new00-project.git")
        print("3. Push to remote: git push -u origin main")
    
    return success

if __name__ == "__main__":
    commit_changes()
