#!/usr/bin/env python3
import shutil
import subprocess
import os

# Test different ways to find LibreOffice
print("Testing LibreOffice detection...")

# Method 1: shutil.which
print("1. Using shutil.which('soffice'):", shutil.which('soffice'))
print("2. Using shutil.which('soffice.exe'):", shutil.which('soffice.exe'))

# Method 2: Direct path check
direct_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
print("3. Direct path check:", os.path.isfile(direct_path))

# Method 4: where command
try:
    result = subprocess.run(["where", "soffice"], capture_output=True, text=True, timeout=5)
    print("4. Using where command:", result.stdout.strip())
except Exception as e:
    print("4. where command failed:", e)

# Method 5: Test if we can run it
try:
    result = subprocess.run([direct_path, "--version"], capture_output=True, text=True, timeout=10)
    print("5. Direct execution:", result.stdout.strip() if result.returncode == 0 else "Failed")
except Exception as e:
    print("5. Direct execution failed:", e)

print("\nPATH environment variable:")
print(os.environ.get('PATH', 'Not found'))
