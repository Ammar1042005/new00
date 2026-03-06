#!/usr/bin/env python3
import sys
sys.path.append('.')
from pdf_tools import _which

print("Testing updated _which function...")
result = _which(["soffice", "soffice.exe"], "libreoffice_path")
print("LibreOffice found at:", result)

if result:
    print("SUCCESS: LibreOffice detection is working!")
else:
    print("FAILED: Still cannot find LibreOffice")
