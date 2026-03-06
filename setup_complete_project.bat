@echo off
echo ========================================
echo   New00 Complete Project Sharing
echo ========================================
echo.
echo Your project contains:
echo - PDF Tools (main app.py)
echo - Image Tools (i_love_img/ folder)
echo.
echo Choose sharing setup:
echo.
echo 1. Single Repository (All-in-One)
echo 2. Multi-Repository (Recommended)
echo 3. Monorepo Structure (Advanced)
echo 4. Create Complete ZIP
echo 5. Install Git (if not installed)
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto single
if "%choice%"=="2" goto multi
if "%choice%"=="3" goto monorepo
if "%choice%"=="4" goto zip
if "%choice%"=="5" goto installgit
goto end

:single
echo.
echo === SINGLE REPOSITORY SETUP ===
echo.
echo 1. Go to: https://github.com/new
echo 2. Repository name: new00-complete-suite
echo 3. Description: Complete document and image processing suite
echo 4. Include both PDF and Image tools
echo.
echo 5. After Git is installed, run:
echo    cd "c:/Users/kille\Desktop\Project\I_OVpdf\new00"
echo    git init
echo    git add .
echo    git commit -m "Initial commit: Complete document and image processing suite"
echo    git remote add origin https://github.com/YOUR_USERNAME/new00-complete-suite.git
echo    git push -u origin main
echo.
pause
goto end

:multi
echo.
echo === MULTI-REPOSITORY SETUP ===
echo.
echo This is the RECOMMENDED approach for team collaboration
echo.
echo 1. First, setup Image Tools repository:
echo    - Go to: https://github.com/new
echo    - Repository name: i-love-img
echo    - Description: Complete image processing suite with GUI editor
echo.
echo 2. Then, setup Main repository:
echo    - Go to: https://github.com/new  
echo    - Repository name: new00-project
echo    - Description: Main project coordination and PDF tools
echo.
echo 3. After Git is installed, run:
echo.
echo    === Setup Image Tools ===
echo    cd "c:/Users/kille\Desktop\Project\I_OVpdf\new00\i_love_img"
echo    git init
echo    git add .
echo    git commit -m "Initial commit: Complete image processing suite"
echo    git remote add origin https://github.com/YOUR_USERNAME/i-love-img.git
echo    git push -u origin main
echo.
echo    === Setup Main Repository ===
echo    cd "c:/Users/kille\Desktop\Project\I_OVpdf\new00"
echo    git init
echo    git add README.md PROJECT_SHARING.md requirements.txt .gitignore
echo    git commit -m "Initial setup: Project coordination and documentation"
echo    git remote add origin https://github.com/YOUR_USERNAME/new00-project.git
echo    git push -u origin main
echo.
pause
goto end

:monorepo
echo.
echo === MONOREPO SETUP (ADVANCED) ===
echo.
echo This creates a single repository with submodules
echo Recommended for large teams with complex workflows
echo.
echo 1. Create main repository: new00-monorepo
echo 2. After Git is installed, run:
echo    cd "c:/Users/kille\Desktop\Project\I_OVpdf\new00"
echo    git init
echo    git add .
echo    git commit -m "Initial commit: Complete suite with monorepo structure"
echo    git remote add origin https://github.com/YOUR_USERNAME/new00-monorepo.git
echo    git push -u origin main
echo.
echo 3. Add submodules:
echo    git submodule add https://github.com/YOUR_USERNAME/i-love-img.git i_love_img
echo    git commit -m "Add image tools as submodule"
echo    git push origin main
echo.
pause
goto end

:zip
echo.
echo === CREATE COMPLETE PROJECT ZIP ===
echo.
cd "c:/Users/kille\Desktop\Project\I_OVpdf\new00"
powershell -command "Compress-Archive -Path . -DestinationPath ..\new00-complete-project.zip -Force"
echo.
echo Complete project ZIP created at: c:\Users\kille\Desktop\Project\I_OVpdf\new00-complete-project.zip
echo.
echo This ZIP contains:
echo - PDF Tools (app.py, pdf_tools.py)
echo - Image Tools (entire i_love_img/ folder)
echo - Documentation (README.md, guides)
echo - Dependencies (requirements.txt)
echo.
echo You can share this ZIP file via:
echo - Email attachment
echo - Google Drive, Dropbox, OneDrive
echo - WeTransfer, FileMail
echo - Direct file sharing
echo.
pause
goto end

:installgit
echo.
echo === INSTALL GIT ===
echo.
echo Installing Git for Windows...
echo.
echo 1. Opening Git download page...
start https://git-scm.com/download/win
echo.
echo 2. Please run the downloaded installer
echo 3. After installation, restart this script
echo.
pause
goto end

:end
echo.
echo ========================================
echo   For detailed guides, see:
echo   - PROJECT_SHARING.md (Complete project sharing)
echo   - SHARING_GUIDE.md (Image tools sharing)
echo   - GIT_SETUP.md (Git setup instructions)
echo ========================================
echo.
echo   Happy collaborating on your New00 complete project!
echo.
