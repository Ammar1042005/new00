"""
Utility functions for New00 project
"""

import io
import os
import hashlib
import tempfile
import mimetypes
from typing import Union, List, Dict, Any, Tuple, Optional
from datetime import datetime
import json

class FileValidator:
    """File validation utilities"""
    
    @staticmethod
    def is_valid_file(file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Validate uploaded file
        
        Args:
            file_data: Raw file data
            filename: File name
            
        Returns:
            dict: Validation result
        """
        result = {
            'valid': False,
            'error': None,
            'file_info': {}
        }
        
        try:
            # Check file size
            file_size = len(file_data)
            if file_size == 0:
                result['error'] = 'File is empty'
                return result
            
            # Get file extension
            ext = os.path.splitext(filename)[1].lower()
            
            # Validate file type
            file_type = FileValidator._detect_file_type(file_data, ext)
            
            result['file_info'] = {
                'name': filename,
                'size': file_size,
                'size_formatted': FileFormatter.format_file_size(file_size),
                'extension': ext,
                'type': file_type,
                'mime_type': FileValidator.get_mime_type(ext),
                'md5': FileValidator.calculate_md5(file_data),
                'upload_time': datetime.now().isoformat()
            }
            
            result['valid'] = True
            return result
            
        except Exception as e:
            result['error'] = f'File validation error: {str(e)}'
            return result
    
    @staticmethod
    def _detect_file_type(file_data: bytes, extension: str) -> str:
        """Detect file type based on content and extension"""
        # PDF files
        if extension == '.pdf':
            return 'pdf'
        
        # Image files
        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']:
            return 'image'
        
        # Document files
        if extension in ['.docx', '.xlsx', '.pptx']:
            return 'document'
        
        return 'unknown'
    
    @staticmethod
    def get_mime_type(extension: str) -> str:
        """Get MIME type for file extension"""
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.tiff': 'image/tiff',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        }
        return mime_types.get(extension, 'application/octet-stream')
    
    @staticmethod
    def calculate_md5(data: bytes) -> str:
        """Calculate MD5 hash of file data"""
        return hashlib.md5(data).hexdigest()

class FileFormatter:
    """File formatting utilities"""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    @staticmethod
    def generate_filename(original_name: str, suffix: str = "", extension: str = None) -> str:
        """Generate new filename with suffix"""
        name, ext = os.path.splitext(original_name)
        
        if extension:
            ext = extension if not extension.startswith('.') else f'.{extension[1:]}'
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{name}_{suffix}_{timestamp}{ext}"
        
        return new_name
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename

class TempFileManager:
    """Temporary file management"""
    
    def __init__(self):
        self.temp_files = []
    
    def create_temp_file(self, data: bytes, suffix: str = ".tmp") -> str:
        """Create temporary file"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(data)
        temp_file.close()
        
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def create_temp_directory(self) -> str:
        """Create temporary directory"""
        temp_dir = tempfile.mkdtemp()
        self.temp_files.append(temp_dir)
        return temp_dir
    
    def cleanup(self):
        """Clean up all temporary files"""
        for temp_path in self.temp_files:
            try:
                if os.path.isfile(temp_path):
                    os.unlink(temp_path)
                elif os.path.isdir(temp_path):
                    import shutil
                    shutil.rmtree(temp_path)
            except Exception as e:
                print(f"Error cleaning up {temp_path}: {e}")
        
        self.temp_files.clear()
    
    def __del__(self):
        """Cleanup on object deletion"""
        self.cleanup()

class ImageProcessor:
    """Image processing utilities"""
    
    @staticmethod
    def resize_image(image_data: bytes, width: int, height: int, maintain_aspect: bool = True) -> bytes:
        """Resize image with optional aspect ratio maintenance"""
        try:
            from PIL import Image
            
            # Open image
            img = Image.open(io.BytesIO(image_data))
            
            # Calculate new dimensions
            if maintain_aspect:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Save resized image
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=90)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            raise ValueError(f"Error resizing image: {str(e)}")
    
    @staticmethod
    def create_thumbnail(image_data: bytes, size: Tuple[int, int] = (200, 200)) -> bytes:
        """Create thumbnail from image"""
        try:
            from PIL import Image
            
            # Open image
            img = Image.open(io.BytesIO(image_data))
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            raise ValueError(f"Error creating thumbnail: {str(e)}")
    
    @staticmethod
    def get_image_info(image_data: bytes) -> Dict[str, Any]:
        """Get image information"""
        try:
            from PIL import Image
            
            # Open image
            img = Image.open(io.BytesIO(image_data))
            
            return {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                'file_size': len(image_data)
            }
            
        except Exception as e:
            raise ValueError(f"Error getting image info: {str(e)}")

class PDFProcessor:
    """PDF processing utilities"""
    
    @staticmethod
    def get_pdf_info(pdf_data: bytes) -> Dict[str, Any]:
        """Get PDF information"""
        try:
            import fitz  # PyMuPDF
            
            # Open PDF
            pdf_doc = fitz.open(stream=pdf_data, filetype="pdf")
            
            # Extract metadata
            metadata = pdf_doc.metadata
            
            # Get page information
            pages_info = []
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                rect = page.rect
                pages_info.append({
                    'page': page_num + 1,
                    'width': rect.width,
                    'height': rect.height,
                    'rotation': page.rotation,
                    'orientation': 'landscape' if rect.width > rect.height else 'portrait'
                })
            
            pdf_doc.close()
            
            return {
                'total_pages': len(pages_info),
                'metadata': metadata,
                'pages': pages_info,
                'file_size': len(pdf_data),
                'is_encrypted': metadata.get('encrypted', False)
            }
            
        except Exception as e:
            raise ValueError(f"Error getting PDF info: {str(e)}")
    
    @staticmethod
    def extract_text(pdf_data: bytes, pages: List[int] = None) -> str:
        """Extract text from PDF"""
        try:
            import fitz
            
            # Open PDF
            pdf_doc = fitz.open(stream=pdf_data, filetype="pdf")
            
            text = ""
            pages_to_extract = pages if pages else range(len(pdf_doc))
            
            for page_num in pages_to_extract:
                if page_num >= len(pdf_doc):
                    continue
                
                page = pdf_doc[page_num]
                text += page.get_text() + "\n"
            
            pdf_doc.close()
            return text.strip()
            
        except Exception as e:
            raise ValueError(f"Error extracting text: {str(e)}")

class Logger:
    """Logging utilities"""
    
    @staticmethod
    def log_operation(operation: str, file_info: Dict[str, Any], result: str = "success", error: str = None):
        """Log operation with file information"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'file_info': file_info,
            'result': result,
            'error': error
        }
        
        # Write to log file
        try:
            with open('new00_operations.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Error writing to log: {e}")
    
    @staticmethod
    def get_recent_operations(limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent operations from log"""
        operations = []
        
        try:
            if os.path.exists('new00_operations.log'):
                with open('new00_operations.log', 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-limit:]  # Get last N lines
                    
                    for line in lines:
                        try:
                            operations.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error reading operations log: {e}")
        
        return operations

class ResponseHelper:
    """API response utilities"""
    
    @staticmethod
    def success_response(data: Any = None, message: str = "Operation successful") -> Dict[str, Any]:
        """Create success response"""
        response = {
            'success': True,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if data is not None:
            response['data'] = data
        
        return response
    
    @staticmethod
    def error_response(message: str, error_code: str = None, details: Any = None) -> Dict[str, Any]:
        """Create error response"""
        response = {
            'success': False,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if error_code:
            response['error_code'] = error_code
        
        if details:
            response['details'] = details
        
        return response
    
    @staticmethod
    def file_response(file_data: bytes, filename: str, content_type: str = None) -> Tuple[bytes, Dict[str, str]]:
        """Create file download response"""
        if content_type is None:
            content_type = FileValidator.get_mime_type(os.path.splitext(filename)[1])
        
        headers = {
            'Content-Type': content_type,
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(len(file_data))
        }
        
        return file_data, headers

# Global utility functions
def create_directory_if_not_exists(path: str) -> bool:
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {path}: {e}")
        return False

def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
    """Clean up old files in directory"""
    import time
    
    cleaned_count = 0
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    try:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.unlink(file_path)
                        cleaned_count += 1
    
    except Exception as e:
        print(f"Error during cleanup: {e}")
    
    return cleaned_count

def validate_parameters(params: Dict[str, Any], required_params: List[str]) -> Tuple[bool, List[str]]:
    """Validate required parameters"""
    missing_params = []
    
    for param in required_params:
        if param not in params or params[param] is None:
            missing_params.append(param)
    
    return len(missing_params) == 0, missing_params

# Example usage and testing
if __name__ == "__main__":
    # Test file validation
    test_data = b"test file content"
    test_filename = "test.pdf"
    
    validation = FileValidator.is_valid_file(test_data, test_filename)
    print(f"File validation result: {validation}")
    
    # Test file formatting
    formatted_size = FileFormatter.format_file_size(1024 * 1024)
    print(f"Formatted size: {formatted_size}")
    
    # Test filename generation
    new_filename = FileFormatter.generate_filename("document.pdf", "processed")
    print(f"Generated filename: {new_filename}")
    
    # Test temporary file management
    temp_manager = TempFileManager()
    temp_file = temp_manager.create_temp_file(test_data)
    print(f"Created temp file: {temp_file}")
    temp_manager.cleanup()
    print("Temporary files cleaned up")
