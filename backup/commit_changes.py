#!/usr/bin/env python3
"""
Commit all changes to Git repository
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"[{description}]...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"[OK] {description} completed")
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description}: {e}")
        return None

def check_git_status():
    """Check current Git status"""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], 
                          capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def stage_all_files():
    """Stage all modified and new files"""
    print("[STAGING] Staging all files...")
    
    # Get list of new files to add
    new_files = [
        "FEATURES.md",
        "FEATURE_INDEX.md", 
        "PROJECT_SHARING.md",
        "project_config.py",
        "utils.py",
        "pdf_merge.py",
        "pdf_split.py", 
        "pdf_rotate.py",
        "pdf_watermark.py",
        "pdf_compress.py",
        "setup_complete_project.bat",
        "commit_changes.py"
    ]
    
    for file in new_files:
        if os.path.exists(file):
            run_command(f"git add {file}", f"Adding {file}")
    
    # Add all other files
    run_command("git add .", "Adding remaining files")

def create_commit_message():
    """Create comprehensive commit message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    commit_message = f"""feat: Complete modular restructuring with separate feature files

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
- pdf_merge.py - Combine multiple PDFs into one document
- pdf_split.py - Split PDF into individual pages or ranges
- pdf_rotate.py - Rotate PDF pages by specified angles
- pdf_watermark.py - Add text/image watermarks to PDFs
- pdf_compress.py - Reduce PDF file size while maintaining quality

Documentation:
- FEATURES.md - Complete feature overview
- FEATURE_INDEX.md - Detailed file index and structure
- PROJECT_SHARING.md - Complete project sharing guide
- setup_complete_project.bat - Interactive project setup

Benefits:
- Maximum modularity - Each feature in separate file
- Enhanced collaboration - Parallel development support
- Superior scalability - Easy to add new features
- Better testing - Individual feature unit tests
- Professional structure - Industry-standard organization

Technical Improvements:
- Single responsibility principle per file
- Comprehensive error handling and validation
- Type hints and documentation
- Environment-specific configuration
- Operation logging and history tracking

Ready for enterprise-level development and team collaboration.

Committed at: {timestamp}"""
    
    return commit_message

def commit_changes():
    """Main commit process"""
    print("🚀 Starting Git commit process...")
    print("=" * 50)
    
    # Check if Git is available
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git is not installed or not in PATH")
        print("\n📋 To install Git:")
        print("1. Download from: https://git-scm.com/download/win")
        print("2. Run installer with default options")
        print("3. Restart command prompt/PowerShell")
        print("4. Run this script again")
        return False
    
    # Check if we're in a Git repository
    if not os.path.exists(".git"):
        print("❌ Not in a Git repository")
        print("🔄 Initializing Git repository...")
        run_command("git init", "Initializing Git repository")
        
        # Configure Git if not already configured
        try:
            subprocess.run(["git", "config", "user.name", "Shaikh Mohammad Ammar"], 
                       check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", 
                       "86150394+Ammar1042005@users.noreply.github.com"], 
                       check=True, capture_output=True)
            print("✅ Git user configured")
        except subprocess.CalledProcessError:
            print("ℹ️ Git user already configured")
    
    # Check current status
    status = check_git_status()
    if status:
        print(f"📋 Current Git status:\n{status}")
    
    # Stage all files
    stage_all_files()
    
    # Create and execute commit
    commit_message = create_commit_message()
    
    print("\n📝 Commit Message Preview:")
    print("-" * 40)
    print(commit_message)
    print("-" * 40)
    
    # Execute commit
    result = run_command(f'git commit -m "{commit_message}"', "Creating commit")
    
    if result:
        print("\n✅ Commit successful!")
        print(f"📋 Commit hash: {result.stdout.strip()}")
        
        # Show status after commit
        final_status = check_git_status()
        if final_status:
            print(f"\n📋 Status after commit:\n{final_status}")
        else:
            print("\n📋 Working directory clean")
    
    return True

def show_next_steps():
    """Show next steps after successful commit"""
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("=" * 50)
    print()
    print("1. 🌐 Push to Remote Repository:")
    print("   git remote add origin https://github.com/Shaikh-Mohammad-Ammar/new00-project.git")
    print("   git push -u origin main")
    print()
    print("2. 📋 Create GitHub Repository:")
    print("   Go to: https://github.com/new")
    print("   Repository name: new00-project")
    print("   Description: Complete document and image processing suite")
    print()
    print("3. 👥 Team Collaboration:")
    print("   Share repository URL with team members")
    print("   Use multi-repository structure for parallel development")
    print()
    print("4. 📚 Documentation:")
    print("   Update README.md with repository information")
    print("   Create CONTRIBUTING.md for development guidelines")
    print()
    print("5. 🚀 Deployment:")
    print("   Set up GitHub Pages for documentation")
    print("   Configure CI/CD with GitHub Actions")
    print()
    print("📋 For detailed guides, see:")
    print("   - PROJECT_SHARING.md (Complete sharing guide)")
    print("   - FEATURE_INDEX.md (File structure reference)")
    print("   - SHARING_GUIDE.md (Image tools sharing)")

def main():
    """Main function"""
    print("New00 Project - Git Commit Tool")
    print("=" * 50)
    print()
    
    # Try to commit changes
    success = commit_changes()
    
    if success:
        show_next_steps()
    
    print("\n" + "=" * 50)
    print("🎉 Git commit process completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
