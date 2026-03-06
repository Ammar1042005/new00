#!/usr/bin/env python3
"""
Setup script for Git repository initialization
Run this script to initialize Git and create initial commit
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        return None

def setup_git_repo():
    """Initialize Git repository and create initial commit"""
    print("Setting up Git repository for I Love Img project...")
    
    # Check if Git is available
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Git is not installed. Please install Git first:")
        print("   - Download from: https://git-scm.com/download/win")
        print("   - Or use package manager: winget install Git.Git")
        return False
    
    # Initialize Git repository
    if not os.path.exists(".git"):
        run_command("git init", "Initializing Git repository")
    else:
        print("Git repository already exists")
    
    # Add all files
    run_command("git add .", "Adding all files to staging")
    
    # Create initial commit
    commit_message = """Initial commit: Complete I Love Img image processing suite

Features:
- Classic image tools (compress, resize, crop, rotate, convert)
- Advanced GUI editor with canvas-based editing
- Background removal (automatic and color-based)
- Adjustments (brightness, contrast, saturation)
- Effects (blur, sharpen, grayscale, sepia, invert)
- Batch processing capabilities
- Modular architecture with separate tool modules
- Modern responsive UI

Technical:
- Flask backend with REST API
- HTML5 Canvas for real-time editing
- Pillow (PIL) for image processing
- Modular Python structure
- Professional undo/redo system"""
    
    run_command(f'git commit -m "{commit_message}"', "Creating initial commit")
    
    # Create main branch if it doesn't exist
    run_command("git branch -M main", "Setting main branch")
    
    print("\nGit repository setup complete!")
    print("\nNext steps:")
    print("1. Add remote repository: git remote add origin <your-repo-url>")
    print("2. Push to remote: git push -u origin main")
    print("3. Create GitHub repository at: https://github.com/new")
    print("\nRepository structure:")
    print("   ├── app.py              # Main Flask application")
    print("   ├── tools/              # Modular tool structure")
    print("   ├── static/             # Frontend assets")
    print("   ├── templates/          # HTML templates")
    print("   ├── requirements.txt     # Python dependencies")
    print("   ├── README.md          # Project documentation")
    print("   └── .gitignore         # Git ignore rules")
    
    return True

if __name__ == "__main__":
    setup_git_repo()
