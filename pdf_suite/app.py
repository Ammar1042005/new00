"""
PDF Suite Application - Dedicated PDF Processing Flask App
"""

import os
import io
import sys
from flask import Flask, request, send_file, render_template, jsonify
from werkzeug.utils import secure_filename

# Add parent directory to path for shared imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'shared'))

from shared.project_config import get_config
from shared.utils import FileValidator, ResponseHelper
from pdf_merge import merge_pdfs
from pdf_split import split_pdf_each_page, split_pdf_range, split_pdf_by_chunks
from pdf_rotate import rotate_pdf, auto_rotate_pdf
from pdf_watermark import add_text_watermark, add_page_numbers, add_header_footer
from pdf_compress import compress_pdf, compress_pdf_advanced

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Get configuration
config = get_config()
app.config['MAX_CONTENT_LENGTH'] = config.UPLOAD['max_size_bytes']
app.config['UPLOAD_FOLDER'] = config.UPLOAD['folder']

@app.route('/')
def index():
    """PDF Suite main page"""
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    """Merge multiple PDFs"""
    try:
        files = request.files.getlist('files')
        if not files or len(files) < 2:
            return ResponseHelper.error_response('Please provide at least 2 PDF files')
        
        # Validate files
        pdf_files = []
        for file in files:
            if file and FileValidator.is_allowed_file(file.filename, 'pdf'):
                pdf_data = file.read()
                pdf_files.append(pdf_data)
            else:
                return ResponseHelper.error_response(f'Invalid file: {file.filename}')
        
        # Merge PDFs
        merged_pdf = merge_pdfs(pdf_files)
        
        return send_file(
            io.BytesIO(merged_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged.pdf'
        )
        
    except Exception as e:
        return ResponseHelper.error_response(f'Error merging PDFs: {str(e)}')

@app.route('/split', methods=['POST'])
def split():
    """Split PDF into pages"""
    try:
        file = request.files.get('file')
        split_type = request.form.get('type', 'individual')
        
        if not file:
            return ResponseHelper.error_response('Please provide a PDF file')
        
        # Validate file
        if not FileValidator.is_allowed_file(file.filename, 'pdf'):
            return ResponseHelper.error_response(f'Invalid file: {file.filename}')
        
        pdf_data = file.read()
        
        # Split based on type
        if split_type == 'individual':
            split_files = split_pdf_each_page(pdf_data)
        elif split_type == 'range':
            page_range = request.form.get('range', '1-5')
            ranges = parse_page_ranges(page_range)
            split_files = split_pdf_range(pdf_data, ranges)
        elif split_type == 'chunks':
            chunk_size = int(request.form.get('chunk_size', '5'))
            split_files = split_pdf_by_chunks(pdf_data, chunk_size)
        else:
            return ResponseHelper.error_response('Invalid split type')
        
        # Create ZIP with split files
        import zipfile
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for i, split_pdf in enumerate(split_files):
                zip_file.writestr(f'split_{i+1}.pdf', split_pdf)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='split_pdfs.zip'
        )
        
    except Exception as e:
        return ResponseHelper.error_response(f'Error splitting PDF: {str(e)}')

def parse_page_ranges(range_string):
    """Parse page range string"""
    ranges = []
    for part in range_string.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            try:
                ranges.append((int(start.strip()), int(end.strip())))
            except ValueError:
                continue
        else:
            try:
                page = int(part)
                ranges.append((page, page))
            except ValueError:
                continue
    return ranges

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the app
    port = int(os.environ.get('PORT', 5002))  # Different port from image tools
    print(f"PDF Suite running at http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=config.SERVER['debug'])
