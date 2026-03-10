"""
Categorized PDF Suite Application - Organized by functionality
"""

import os
import io
import sys
from flask import Flask, request, send_file, render_template, jsonify
from werkzeug.utils import secure_filename
from categorized_pdf_tools import *

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'pdf-suite-categorized-secret-key'

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# =============================================================================
# MAIN ROUTES
# =============================================================================

@app.route('/')
def index():
    """Main page - categorized PDF tools"""
    return render_template('index_categorized.html', 
                         max_file_size_display="100MB")


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "categorized",
        "categories": [
            "information",
            "manipulation", 
            "content",
            "conversion",
            "compression",
            "text",
            "security",
            "utility"
        ]
    })


# =============================================================================
# PDF INFORMATION & VALIDATION ROUTES
# =============================================================================

@app.route('/api/pdf-info', methods=['POST'])
def get_pdf_info_endpoint():
    """Get PDF information"""
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": "Invalid file format"}), 400
        
        # Read file
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Get PDF info
        info = get_pdf_info(pdf_data)
        
        return jsonify({
            "success": True,
            "info": info,
            "file_name": file.filename,
            "file_size_display": f"{len(pdf_data)/1024/1024:.1f}MB"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/validate-page-range', methods=['POST'])
def validate_page_range_endpoint():
    """Validate page range"""
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


# =============================================================================
# PDF MANIPULATION ROUTES
# =============================================================================

@app.route('/api/merge', methods=['POST'])
def merge_pdfs_endpoint():
    """Merge multiple PDFs"""
    try:
        files = request.files.getlist('files')
        if not files or len(files) < 2:
            return jsonify({"success": False, "error": "Please provide at least 2 PDF files"}), 400
        
        # Validate and collect files
        pdf_files = []
        file_names = []
        for file in files:
            if file and file.filename.lower().endswith('.pdf'):
                pdf_data = file.read()
                validate_file_size(pdf_data)
                pdf_files.append(pdf_data)
                file_names.append(file.filename)
            else:
                return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        # Merge PDFs
        merged_pdf = merge_pdfs_categorized(pdf_files)
        
        return send_file(
            io.BytesIO(merged_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged.pdf'
        )
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error merging PDFs: {str(e)}"}), 500


@app.route('/api/split', methods=['POST'])
def split_pdf_endpoint():
    """Split PDF into page range"""
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
                    "error": f"Invalid page range: {', '.join(validation['errors'])}"
                }), 400
            
            # Split PDF
            split_pdf_data = split_pdf_categorized(pdf_data, from_page, to_page)
            
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
            extracted_pdf = extract_pages_categorized(pdf_data, pages)
            
            return send_file(
                io.BytesIO(extracted_pdf),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'extracted_pages_{"_".join(map(str, pages))}.pdf'
            )
            
        else:
            return jsonify({"success": False, "error": "Invalid split type"}), 400
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error splitting PDF: {str(e)}"}), 500


@app.route('/api/rotate', methods=['POST'])
def rotate_pdf_endpoint():
    """Rotate PDF pages"""
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
        rotated_pdf = rotate_pdf_categorized(pdf_data, angle, page_range)
        
        return send_file(
            io.BytesIO(rotated_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='rotated.pdf'
        )
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error rotating PDF: {str(e)}"}), 500


# =============================================================================
# PDF CONTENT MODIFICATION ROUTES
# =============================================================================

@app.route('/api/add-page-numbers', methods=['POST'])
def add_page_numbers_endpoint():
    """Add page numbers to PDF"""
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
        numbered_pdf = add_page_numbers_categorized(
            pdf_data, format_string, position, font_size, start_page
        )
        
        return send_file(
            io.BytesIO(numbered_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='page_numbers.pdf'
        )
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error adding page numbers: {str(e)}"}), 500


@app.route('/api/add-watermark', methods=['POST'])
def add_watermark_endpoint():
    """Add watermark to PDF"""
    try:
        file = request.files.get('file')
        watermark_text = request.form.get('watermark_text', 'WATERMARK')
        position = request.form.get('position', 'center')
        opacity = float(request.form.get('opacity', 0.3))
        rotation = int(request.form.get('rotation', 45))
        font_size = int(request.form.get('font_size', 48))
        
        if not file:
            return jsonify({"success": False, "error": "Please provide a PDF file"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Add watermark
        watermarked_pdf = add_watermark_categorized(
            pdf_data, watermark_text, position, opacity, rotation, font_size
        )
        
        return send_file(
            io.BytesIO(watermarked_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='watermarked.pdf'
        )
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error adding watermark: {str(e)}"}), 500


# =============================================================================
# PDF CONVERSION ROUTES
# =============================================================================

@app.route('/api/convert-to-images', methods=['POST'])
def pdf_to_images_endpoint():
    """Convert PDF to images"""
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
        images = pdf_to_images_categorized(pdf_data, dpi, format_type)
        
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
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error converting PDF to images: {str(e)}"}), 500


@app.route('/api/extract-images', methods=['POST'])
def extract_images_endpoint():
    """Extract images from PDF"""
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
        extracted_images = extract_images_categorized(pdf_data)
        
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
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error extracting images: {str(e)}"}), 500


# =============================================================================
# PDF COMPRESSION ROUTES
# =============================================================================

@app.route('/api/compress', methods=['POST'])
def compress_pdf_endpoint():
    """Compress PDF file"""
    try:
        file = request.files.get('file')
        method = request.form.get('method', 'standard')
        
        if not file:
            return jsonify({"success": False, "error": "Please provide a PDF file"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Create temporary files
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_input:
            temp_input.write(pdf_data)
            temp_input_path = temp_input.name
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_output:
            temp_output_path = temp_output.name
        
        try:
            # Use the working compression method
            from final_working_compression import compress_pdf_simple
            success = compress_pdf_simple(temp_input_path, temp_output_path)
            
            if not success:
                return jsonify({
                    "success": False,
                    "error": "Unable to compress this PDF. The file may already be optimally compressed.",
                    "original_size": len(pdf_data),
                    "note": "This PDF may contain mostly text or already be compressed."
                }), 400
            
            # Read the compressed file
            with open(temp_output_path, 'rb') as f:
                compressed_pdf = f.read()
            
            compressed_size = len(compressed_pdf)
            compression_ratio = (1 - compressed_size / len(pdf_data)) * 100
            
            # Verify compression actually reduced size
            if compressed_size >= len(pdf_data):
                return jsonify({
                    "success": False,
                    "error": "Compression did not reduce file size.",
                    "original_size": len(pdf_data),
                    "compressed_size": compressed_size
                }), 400
            
            return send_file(
                io.BytesIO(compressed_pdf),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='compressed.pdf'
            )
            
        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_input_path)
                os.unlink(temp_output_path)
            except:
                pass
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error compressing PDF: {str(e)}"}), 500


# =============================================================================
# PDF TEXT PROCESSING ROUTES
# =============================================================================

@app.route('/api/extract-text', methods=['POST'])
def extract_text_endpoint():
    """Extract text from PDF"""
    try:
        file = request.files.get('file')
        page_numbers = request.form.get('page_numbers', '')
        
        if not file:
            return jsonify({"success": False, "error": "Please provide a PDF file"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Parse page numbers if provided
        pages = None
        if page_numbers.strip():
            try:
                pages = [int(p.strip()) for p in page_numbers.split(',')]
            except ValueError:
                return jsonify({"success": False, "error": "Invalid page numbers format"}), 400
        
        # Extract text
        text = extract_text_categorized(pdf_data, pages)
        
        return jsonify({
            "success": True,
            "text": text,
            "character_count": len(text),
            "word_count": len(text.split()) if text else 0
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error extracting text: {str(e)}"}), 500


@app.route('/api/search-text', methods=['POST'])
def search_text_endpoint():
    """Search for text in PDF"""
    try:
        file = request.files.get('file')
        search_term = request.form.get('search_term', '')
        case_sensitive = request.form.get('case_sensitive', 'false').lower() == 'true'
        
        if not file:
            return jsonify({"success": False, "error": "Please provide a PDF file"}), 400
        
        if not search_term.strip():
            return jsonify({"success": False, "error": "Please provide a search term"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Search text
        results = search_text_categorized(pdf_data, search_term, case_sensitive)
        
        return jsonify({
            "success": True,
            "search_term": search_term,
            "results_count": len(results),
            "results": results
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error searching text: {str(e)}"}), 500


# =============================================================================
# PDF SECURITY ROUTES
# =============================================================================

@app.route('/api/encrypt', methods=['POST'])
def encrypt_pdf_endpoint():
    """Encrypt PDF with password"""
    try:
        file = request.files.get('file')
        password = request.form.get('password', '')
        owner_password = request.form.get('owner_password', '')
        
        if not file:
            return jsonify({"success": False, "error": "Please provide a PDF file"}), 400
        
        if not password.strip():
            return jsonify({"success": False, "error": "Please provide a password"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Encrypt PDF
        encrypted_pdf = encrypt_pdf_categorized(
            pdf_data, password, owner_password if owner_password.strip() else None
        )
        
        return send_file(
            io.BytesIO(encrypted_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='encrypted.pdf'
        )
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error encrypting PDF: {str(e)}"}), 500


@app.route('/api/decrypt', methods=['POST'])
def decrypt_pdf_endpoint():
    """Decrypt PDF"""
    try:
        file = request.files.get('file')
        password = request.form.get('password', '')
        
        if not file:
            return jsonify({"success": False, "error": "Please provide a PDF file"}), 400
        
        if not password.strip():
            return jsonify({"success": False, "error": "Please provide a password"}), 400
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": f"Invalid file: {file.filename}"}), 400
        
        pdf_data = file.read()
        validate_file_size(pdf_data)
        
        # Decrypt PDF
        decrypted_pdf = decrypt_pdf_categorized(pdf_data, password)
        
        return send_file(
            io.BytesIO(decrypted_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='decrypted.pdf'
        )
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error decrypting PDF: {str(e)}"}), 500


# =============================================================================
# UTILITY ROUTES
# =============================================================================

@app.route('/api/create-blank', methods=['POST'])
def create_blank_pdf_endpoint():
    """Create blank PDF"""
    try:
        page_count = int(request.form.get('page_count', 1))
        page_size = request.form.get('page_size', 'A4')
        
        # Create blank PDF
        blank_pdf = create_blank_pdf_categorized(page_count, page_size)
        
        return send_file(
            io.BytesIO(blank_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'blank_{page_count}_pages.pdf'
        )
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error creating blank PDF: {str(e)}"}), 500


@app.route('/api/compare', methods=['POST'])
def compare_pdfs_endpoint():
    """Compare two PDFs"""
    try:
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')
        
        if not file1 or not file2:
            return jsonify({"success": False, "error": "Please provide two PDF files to compare"}), 400
        
        # Validate files
        if not file1.filename.lower().endswith('.pdf') or not file2.filename.lower().endswith('.pdf'):
            return jsonify({"success": False, "error": "Both files must be PDFs"}), 400
        
        pdf1_data = file1.read()
        pdf2_data = file2.read()
        
        validate_file_size(pdf1_data)
        validate_file_size(pdf2_data)
        
        # Compare PDFs
        comparison = compare_pdfs_categorized(pdf1_data, pdf2_data)
        
        return jsonify({
            "success": True,
            "comparison": comparison,
            "file1_name": file1.filename,
            "file2_name": file2.filename
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error comparing PDFs: {str(e)}"}), 500


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        "success": False,
        "error": "File too large. Maximum size is 100MB",
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


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Categorized PDF Suite running at http://localhost:{port}")
    print("Available categories:")
    print("  - Information & Validation")
    print("  - PDF Manipulation")
    print("  - Content Modification")
    print("  - PDF Conversion")
    print("  - PDF Compression")
    print("  - Text Processing")
    print("  - PDF Security")
    print("  - Utility Functions")
    app.run(host='0.0.0.0', port=port, debug=True)
