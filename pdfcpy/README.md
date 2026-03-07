# PDF Suite - Complete Document Processing Platform

A comprehensive web-based PDF processing application with advanced document manipulation capabilities, built with Flask and modern web technologies.

## 🚀 Features

### **PDF Processing Tools**
- **Merge** - Combine multiple PDFs into one document
- **Split** - Split PDF into individual pages or ranges
- **Rotate** - Rotate PDF pages by specified angles
- **Compress** - Reduce PDF file size while maintaining quality
- **Watermark** - Add text/image watermarks and page numbers
- **OCR** - Extract text from scanned PDFs
- **Convert** - Convert between PDF and other formats
- **Password Protection** - Add/remove PDF security

### **Advanced Features**
- **Batch Processing** - Handle multiple documents simultaneously
- **Metadata Editing** - Modify document properties
- **Page Extraction** - Extract specific pages
- **Format Conversion** - PDF ↔ Word, Excel, PowerPoint
- **Digital Signatures** - Add electronic signatures
- **Form Filling** - Interactive PDF form processing

## 🛠️ Technical Stack

### **Backend**
- **Flask** - Web framework
- **PyMuPDF (fitz)** - PDF processing
- **pypdf** - PDF manipulation
- **reportlab** - PDF generation
- **pytesseract** - OCR functionality
- **LibreOffice** - Document conversion

### **Frontend**
- **Modern HTML5** - Responsive design
- **JavaScript ES6+** - Interactive features
- **CSS3** - Modern styling
- **Drag & Drop** - Intuitive file upload
- **Progress Indicators** - Real-time feedback

### **Architecture**
```
pdfcpy/
├── app.py                 # Main Flask application
├── pdf_tools.py          # PDF processing functions
├── config.py             # Configuration management
├── shared/               # Shared utilities
│   ├── project_config.py # Project settings
│   └── utils.py          # Helper functions
├── static/
│   ├── css/
│   │   └── style.css     # Modern styling
│   └── js/
│       └── main.js       # Interactive features
├── templates/
│   └── index.html        # Main interface
└── requirements.txt       # Dependencies
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- pip (Python package manager)
- **LibreOffice** (for document conversion)
- **Tesseract OCR** (for text extraction)

### **Required Tools Setup**

#### **📄 LibreOffice Installation**
LibreOffice is required for PDF ↔ Office document conversion.

**Windows Installation:**
```bash
# Download and install LibreOffice
# Visit: https://www.libreoffice.org/download/download-libreoffice/

# OR using Chocolatey package manager
choco install libreoffice

# OR using Windows Package Manager
winget install TheDocumentFoundation.LibreOffice
```

**macOS Installation:**
```bash
# Using Homebrew
brew install --cask libreoffice

# OR download from https://www.libreoffice.org/download/download-libreoffice/
```

**Linux Installation:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install libreoffice

# Fedora
sudo dnf install libreoffice

# Arch Linux
sudo pacman -S libreoffice-fresh
```

#### **🔍 Tesseract OCR Installation**
Tesseract is required for text extraction from scanned PDFs.

**Windows Installation:**
```bash
# Using Chocolatey
choco install tesseract

# OR using Windows Package Manager
winget install UglyToad.Tesseract

# OR download from https://github.com/UB-Mannheim/tesseract/wiki
```

**macOS Installation:**
```bash
# Using Homebrew
brew install tesseract
```

**Linux Installation:**
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr

# Fedora
sudo dnf install tesseract

# Arch Linux
sudo pacman -S tesseract
```

#### **🌐 Additional Language Support**
For OCR in different languages, install language packs:

**Windows:**
```bash
# Download language data from https://github.com/tesseract-ocr/tessdata
# Copy .traineddata files to C:\Program Files\Tesseract-OCR\tessdata
```

**macOS/Linux:**
```bash
# Install specific language packs (example for Spanish)
sudo apt install tesseract-ocr-spa  # Ubuntu/Debian
brew install tesseract-lang         # macOS (includes all languages)
```

#### **📋 Tool Verification**
Verify installations before running the application:

```bash
# Check LibreOffice
libreoffice --version

# Check Tesseract
tesseract --version

# Check Python dependencies
pip list | grep -E "(PyMuPDF|pypdf|pytesseract)"
```

### **Installation**
```bash
# Clone the repository
git clone <repository-url>
cd new00/pdfcpy

# Install Python dependencies
pip install -r requirements.txt

# Verify all tools are installed
python -c "import fitz, pytesseract; print('All dependencies installed successfully')"

# Run the application
python app.py
```

### **Access Points**
- **Main Interface**: http://localhost:5000
- **API Endpoints**: http://localhost:5000/api/

## 📋 API Endpoints

### **PDF Operations**
- `POST /merge` - Merge multiple PDFs
- `POST /split` - Split PDF into pages
- `POST /rotate` - Rotate PDF pages
- `POST /compress` - Compress PDF file
- `POST /watermark` - Add watermark to PDF
- `POST /ocr` - Extract text from PDF
- `POST /convert` - Convert PDF format
- `POST /protect` - Add password protection

### **Document Conversion**
- `POST /convert-to-word` - PDF to Word
- `POST /convert-to-excel` - PDF to Excel
- `POST /convert-to-powerpoint` - PDF to PowerPoint
- `POST /convert-from-word` - Word to PDF
- `POST /convert-from-excel` - Excel to PDF
- `POST /convert-from-powerpoint` - PowerPoint to PDF

### **Utilities**
- `POST /extract-pages` - Extract specific pages
- `POST /add-page-numbers` - Add page numbering
- `POST /metadata` - Get/edit PDF metadata
- `POST /validate` - Validate PDF integrity

## 🎨 Usage Examples

### **PDF Merge**
```javascript
// Merge multiple PDFs
const formData = new FormData();
files.forEach(file => formData.append('files', file));

fetch('/merge', {
    method: 'POST',
    body: formData
}).then(response => response.blob())
  .then(blob => downloadPDF(blob, 'merged.pdf'));
```

### **PDF Split**
```javascript
// Split PDF into individual pages
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('type', 'individual');

fetch('/split', {
    method: 'POST',
    body: formData
}).then(response => response.blob())
  .then(blob => downloadPDF(blob, 'split_pdfs.zip'));
```

### **PDF Compression**
```javascript
// Compress PDF with quality settings
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('quality', 'medium');
formData.append('image_quality', '75');

fetch('/compress', {
    method: 'POST',
    body: formData
}).then(response => response.blob())
  .then(blob => downloadPDF(blob, 'compressed.pdf'));
```

## 🔧 Configuration

### **Environment Variables**
```bash
PORT=5000                    # Server port
MAX_CONTENT_LENGTH=209715200 # Max upload size (200MB)
UPLOAD_FOLDER=./uploads      # Upload directory
```

### **Settings**
- **Default Quality**: Medium compression
- **OCR Language**: English
- **Conversion Timeout**: 60 seconds
- **Supported Formats**: PDF, DOCX, XLSX, PPTX

## 🛠️ Troubleshooting

### **Common Issues & Solutions**

#### **📄 LibreOffice Issues**

**Problem: "libreoffice command not found"**
```bash
# Solution: Add LibreOffice to PATH
# Windows: Add to System Environment Variables
# macOS/Linux: Add to ~/.bashrc or ~/.zshrc
export PATH="/Applications/LibreOffice.app/Contents/MacOS:$PATH"  # macOS
export PATH="/usr/bin/libreoffice:$PATH"  # Linux
```

**Problem: Document conversion fails**
```bash
# Solution: Check LibreOffice headless mode
libreoffice --headless --convert-to pdf test.docx

# If fails, try:
libreoffice --headless --invisible --nodefault --nolockcheck --nonetwork --nologo --norestore --convert-to pdf test.docx
```

**Problem: LibreOffice not accessible from Python**
```bash
# Solution: Verify LibreOffice is in PATH
python -c "import subprocess; print(subprocess.run(['libreoffice', '--version'], capture_output=True).stdout.decode())"
```

#### **🔍 Tesseract OCR Issues**

**Problem: "tesseract command not found"**
```bash
# Solution: Add Tesseract to PATH
# Windows: Add C:\Program Files\Tesseract-OCR to PATH
# macOS/Linux: Usually added automatically
export PATH="/usr/local/bin:$PATH"  # macOS
export PATH="/usr/bin:$PATH"  # Linux
```

**Problem: "tesseract data not found"**
```bash
# Solution: Install language data
# Windows: Download .traineddata files to tessdata directory
# macOS/Linux: Install language packages
sudo apt install tesseract-ocr-eng  # English
sudo apt install tesseract-ocr-spa  # Spanish
```

**Problem: OCR returns empty text**
```bash
# Solution: Check image quality and language settings
python -c "
import pytesseract
from PIL import Image
print('Tesseract version:', pytesseract.get_tesseract_version())
print('Available languages:', pytesseract.get_languages(config=''))
"
```

#### **🐍 Python Dependency Issues**

**Problem: PyMuPDF installation fails**
```bash
# Solution: Install system dependencies first
# Ubuntu/Debian:
sudo apt install python3-dev libmupdf-dev

# Then install PyMuPDF
pip install PyMuPDF
```

**Problem: pytesseract can't find Tesseract**
```bash
# Solution: Set Tesseract path explicitly
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux
```

#### **🌐 Network & Permission Issues**

**Problem: LibreOffice can't access files**
```bash
# Solution: Check file permissions
chmod 644 input_file.docx
chmod 755 output_directory/

# For Windows: Ensure read/write permissions
icacls "C:\path\to\file" /grant Users:F
```

**Problem: Port already in use**
```bash
# Solution: Change port or kill existing process
netstat -tulpn | grep :5000  # Find process using port
kill -9 <PID>  # Kill process

# OR change port in environment variables
export PORT=5001
python app.py
```

### **🔧 Performance Optimization**

#### **LibreOffice Performance**
```bash
# Limit memory usage
export SAL_USE_VCLPLUGIN=gen
export LIBREOFFICE_JAVA_HOME=/path/to/java

# Disable unnecessary features
libreoffice --headless --norestore --nodefault --nolockcheck --nonetwork --convert-to pdf input.docx
```

#### **OCR Performance**
```bash
# Optimize Tesseract settings
export OMP_THREAD_LIMIT=4  # Limit CPU threads
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/  # Set data path
```

#### **Memory Management**
```python
# In Python: Clean up temporary files
import tempfile
import os

def cleanup_temp_files():
    temp_dir = tempfile.gettempdir()
    for file in os.listdir(temp_dir):
        if file.startswith('tmp') and file.endswith('.pdf'):
            os.remove(os.path.join(temp_dir, file))
```

## 🎯 Key Features

### **Advanced PDF Processing**
- **High-Quality Compression**: Maintain document quality
- **Intelligent OCR**: Accurate text extraction
- **Format Preservation**: Keep original formatting
- **Batch Operations**: Process multiple files
- **Security Features**: Password protection and encryption

### **Document Conversion**
- **Format Support**: PDF ↔ Office formats
- **Layout Preservation**: Maintain document structure
- **Image Handling**: Process embedded images
- **Font Embedding**: Preserve typography
- **Metadata Transfer**: Copy document properties

### **User Experience**
- **Drag & Drop**: Intuitive file upload
- **Progress Tracking**: Real-time feedback
- **Error Handling**: Clear error messages
- **Mobile Responsive**: Works on all devices
- **Offline Capable**: 100% offline functionality

## 🧪 Development

### **Modular Structure**
Each PDF function is organized in `pdf_tools.py`:
- `merge_pdfs()` - Combine multiple PDFs
- `split_pdf()` - Split PDF into pages
- `rotate_pdf()` - Rotate PDF pages
- `compress_pdf()` - Reduce file size
- `add_watermark()` - Add watermarks
- `extract_text_ocr()` - OCR text extraction

### **Adding New Tools**
1. Create function in `pdf_tools.py`
2. Add endpoint in `app.py`
3. Update frontend interface
4. Add error handling
5. Test thoroughly

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Add tests if applicable
5. Submit pull request

## 📞 Support

For issues, questions, or contributions:
- Create an issue in the repository
- Check existing documentation
- Review code examples

---

**Built with ❤️ using Flask, PyMuPDF, and modern web technologies**
