@echo off
echo ========================================
echo   I Love Img - Project Sharing
echo ========================================
echo.
echo Choose sharing option:
echo.
echo 1. GitHub Repository (Recommended)
echo 2. GitLab Repository
echo 3. Create ZIP for sharing
echo 4. Install Git (if not installed)
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto github
if "%choice%"=="2" goto gitlab
if "%choice%"=="3" goto zip
if "%choice%"=="4" goto installgit
goto end

:github
echo.
echo Setting up GitHub repository...
echo.
echo 1. Go to: https://github.com/new
echo 2. Repository name: i-love-img
echo 3. Description: Complete image processing suite with GUI editor
echo 4. Choose Public or Private visibility
echo 5. Click 'Create repository'
echo.
echo 6. After Git is installed, run:
echo    cd "c:/Users/kille\Desktop\Project\I_OVpdf\new00"
echo    git remote add origin https://github.com/YOUR_USERNAME/i-love-img.git
echo    git push -u origin main
echo.
pause
goto end

:gitlab
echo.
echo Setting up GitLab repository...
echo.
echo 1. Go to: https://gitlab.com/projects/new
echo 2. Project name: i-love-img
echo 3. Choose Public or Private
echo 4. Click 'Create project'
echo.
echo 5. After Git is installed, run:
echo    cd "c:/Users/kille\Desktop\Project\I_OVpdf\new00"
echo    git remote add origin https://gitlab.com/YOUR_USERNAME/i-love-img.git
echo    git push -u origin main
echo.
pause
goto end

:zip
echo.
echo Creating project ZIP for sharing...
echo.
cd "c:/Users/kille\Desktop\Project\I_OVpdf\new00"
powershell -command "Compress-Archive -Path . -DestinationPath ..\i-love-img.zip -Force"
echo.
echo ZIP created at: c:\Users\kille\Desktop\Project\I_OVpdf\i-love-img.zip
echo You can share this ZIP file via email, cloud storage, or file sharing services.
echo.
pause
goto end

:installgit
echo.
echo Installing Git for Windows...
echo.
echo 1. Downloading Git installer...
echo Opening download page in browser...
start https://git-scm.com/download/win
echo.
echo 2. Please run the downloaded installer
echo 3. After installation, run: python setup_git.py
echo.
pause
goto end

:end
echo.
echo For detailed sharing guide, see: SHARING_GUIDE.md
echo.
echo Happy collaborating on your I Love Img project!
echo.
