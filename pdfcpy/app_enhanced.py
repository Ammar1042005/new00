"""
Enhanced PDF Suite Application - With improvements based on test report
"""

import os
import io
import sys
from flask import Flask, request, send_file, render_template, jsonify
from werkzeug.utils import secure_filename
from enhanced_pdf_tools import (
    merge_pdfs_enhanced, 
    split_pdf_enhanced, 
    extract_pages_enhanced,
    rotate_pdf_enhanced,
    pdf_to_images_enhanced,
    extract_images_enhanced,
    add_page_numbers_enhanced,
    get_pdf_info,
    validate_file_size,
    validate_page_range,
    PDFProcessingError,
    safe_pdf_operation,
    MAX_FILE_SIZE
)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuration
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'pdf-suite-enhanced-secret-key'

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Enhanced PDF Suite main page"""
    return render_template('index.html', 
                         max_file_size=MAX_FILE_SIZE,
                         max_file_size_display=f"{MAX_FILE_SIZE/1024/1024:.0f}MB")


@app.route('/api/pdf-info', methods=['POST'])
def get_pdf_info_endpoint():
    """Get PDF information with validation"""
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": "Invalid file format"}), 400
        
        # Read file
        pdf_data = file.read()
        
        # Get PDF info
        info = get_pdf_info(pdf_data)
        
        return jsonify({
            "success": True,
            "info": info,
            "file_name": file.filename,
            "file_size_display": f"{len(pdf_data)/1024/1024:.1f}MB"
        })
        
    except PDFProcessingError as e:
        return jsonify({"success": False, "error": str(e), "error_code": e.error_code}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Unexpected error: {str(e)}"}), 500


@app.route('/api/merge', methods=['POST'])
def merge_pdfs():
    """Enhanced PDF merge with validation"""
    try:
        files = request.files.getlist('files')
        if not files or len(files) < 2:
            return jsonify({"success": False, "error": "Please provide at least 2 PDF files"}), 400
        
        # Validate files
        pdf_files = []
        file_names = []
        for file in files:
            if file and file.filename.lower().endswith('.pdf'):
                pdf_data = file.read()
                validate_file_size(pdf_data)  # Validate each file
                pdf_files.append(pdf_data)
                file_names.append(file.filename)
            else:
                return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        # Merge PDFs
        merged_pdf = safe_pdf_operation(merge_pdfs_enhanced, pdf_files)
        
        return send_file(
            io.BytesIO(merged_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged.pdf'
        )
        
    except PDFProcessingError as e:
        return jsonify({"success": False, "error": str(e), "error_code": e.error_code}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Error merging PDFs: {str(e)}"}), 500


@app.route('/api/split', methods=['POST'])
def split_pdf():
    """Enhanced PDF split with validation"""
    try:
        file = request.files.get('file')
        split_type = request.form.get('type', 'range')
        
        if not file:
            return jsonify({"success": False, "error": "Please provide a PDF file"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Get PDF info for validation
        info = get_pdf_info(pdf_data)
        total_pages = info['page_count']
        
        if split_type == 'range':
            from_page = int(request.form.get('from_page', 1))
            to_page = int(request.form.get('to_page', total_pages))
            
            # Validate page range
            validation = validate_page_range(from_page, to_page, total_pages)
            if not validation['valid']:
                return jsonify({
                    "success": False, 
                    "error": f"Invalid page range: {', '.join(validation['errors'])}",
                    "error_code": "INVALID_PAGE_RANGE"
                }), 400
            
            # Split PDF
            split_pdf_data = safe_pdf_operation(split_pdf_enhanced, pdf_data, from_page, to_page)
            
            return send_file(
                io.BytesIO(split_pdf_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'split_pages_{from_page}-{to_page}.pdf'
            )
            
        elif split_type == 'extract':
            page_numbers = request.form.get('pages', '').strip()
            if not page_numbers:
                return jsonify({"success": False, "error": "Please provide page numbers to extract"}), 400
            
            # Parse page numbers
            try:
                pages = [int(p.strip()) for p in page_numbers.split(',')]
            except ValueError:
                return jsonify({"success": False, "error": "Invalid page numbers format"}), 400
            
            # Extract pages
            extracted_pdf = safe_pdf_operation(extract_pages_enhanced, pdf_data, pages)
            
            return send_file(
                io.BytesIO(extracted_pdf),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'extracted_pages_{"_".join(map(str, pages))}.pdf'
            )
            
        else:
            return jsonify({"success": False, "error": "Invalid split type"}), 400
        
    except PDFProcessingError as e:
        return jsonify({"success": False, "error": str(e), "error_code": e.error_code}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Error splitting PDF: {str(e)}"}), 500


@app.route('/api/rotate', methods=['POST'])
def rotate_pdf():
    """Enhanced PDF rotation with validation"""
    try:
        file = request.files.get('file')
        angle = int(request.form.get('angle', 90))
        page_range = request.form.get('page_range', 'all')
        
        if not file:
            return jsonify({"success": False, "error": "Please provide a PDF file"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Rotate PDF
        rotated_pdf = safe_pdf_operation(rotate_pdf_enhanced, pdf_data, angle, page_range)
        
        return send_file(
            io.BytesIO(rotated_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='rotated.pdf'
        )
        
    except PDFProcessingError as e:
        return jsonify({"success": False, "error": str(e), "error_code": e.error_code}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Error rotating PDF: {str(e)}"}), 500


@app.route('/api/add-page-numbers', methods=['POST'])
def add_page_numbers():
    """Enhanced page numbering with large file support"""
    try:
        file = request.files.get('file')
        format_string = request.form.get('format', 'Page {n}')
        position = request.form.get('position', 'bottom-center')
        font_size = int(request.form.get('font_size', 12))
        start_page = int(request.form.get('start_page', 1))
        
        if not file:
            return jsonify({"success": False, "error": "Please provide a PDF file"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Add page numbers
        numbered_pdf = safe_pdf_operation(
            add_page_numbers_enhanced, 
            pdf_data, 
            format_string, 
            position, 
            font_size, 
            start_page
        )
        
        return send_file(
            io.BytesIO(numbered_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='page_numbers.pdf'
        )
        
    except PDFProcessingError as e:
        return jsonify({"success": False, "error": str(e), "error_code": e.error_code}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Error adding page numbers: {str(e)}"}), 500


@app.route('/api/convert-to-images', methods=['POST'])
def pdf_to_images():
    """Enhanced PDF to image conversion"""
    try:
        file = request.files.get('file')
        dpi = int(request.form.get('dpi', 150))
        format_type = request.form.get('format', 'PNG')
        
        if not file:
            return jsonify({"success": False, "error": "Please provide a PDF file"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Convert to images
        images = safe_pdf_operation(pdf_to_images_enhanced, pdf_data, dpi, format_type)
        
        # Create ZIP file with images
        import zipfile
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for i, image_data in enumerate(images):
                zip_file.writestr(f'page_{i+1}.{format_type.lower()}', image_data)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='pdf_images.zip'
        )
        
    except PDFProcessingError as e:
        return jsonify({"success": False, "error": str(e), "error_code": e.error_code}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Error converting PDF to images: {str(e)}"}), 500


@app.route('/api/extract-images', methods=['POST'])
def extract_images():
    """Enhanced image extraction from PDF"""
    try:
        file = request.files.get('file')
        
        if not file:
            return jsonify({"success": False, "error": "Please provide a PDF file"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Extract images
        extracted_images = safe_pdf_operation(extract_images_enhanced, pdf_data)
        
        if not extracted_images:
            return jsonify({"success": False, "error": "No images found in PDF"}), 400
        
        # Create ZIP file with extracted images
        import zipfile
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for image_data, filename in extracted_images:
                zip_file.writestr(filename, image_data)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='extracted_images.zip'
        )
        
    except PDFProcessingError as e:
        return jsonify({"success": False, "error": str(e), "error_code": e.error_code}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Error extracting images: {str(e)}"}), 500


@app.route('/api/validate-page-range', methods=['POST'])
def validate_page_range_endpoint():
    """Validate page range before processing"""
    try:
        data = request.get_json()
        from_page = int(data.get('from_page', 1))
        to_page = int(data.get('to_page', 1))
        total_pages = int(data.get('total_pages', 1))
        
        validation = validate_page_range(from_page, to_page, total_pages)
        
        return jsonify(validation)
        
    except (ValueError, TypeError):
        return jsonify({
            "valid": False,
            "errors": ["Please enter valid page numbers"]
        })


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        "success": False,
        "error": f"File too large. Maximum size is {MAX_FILE_SIZE/1024/1024:.0f}MB",
        "error_code": "FILE_TOO_LARGE"
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error. Please try again.",
        "error_code": "INTERNAL_ERROR"
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Enhanced PDF Suite running at http://localhost:{port}")
    print(f"Maximum file size: {MAX_FILE_SIZE/1024/1024:.0f}MB")
    app.run(host='0.0.0.0', port=port, debug=True)
