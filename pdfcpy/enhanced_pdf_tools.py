"""
Enhanced PDF Tools - Improved version with fixes for large files and validation
"""

import fitz  # PyMuPDF
import os
import tempfile
from io import BytesIO
import gc
from typing import List, Union, Dict, Any, Tuple

# Configuration
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
CHUNK_SIZE = 10  # Process pages in chunks of 10


class PDFProcessingError(Exception):
    """Custom exception for PDF processing errors"""
    def __init__(self, message: str, error_code: str = None, details: str = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details


class LargePDFProcessor:
    """Handles large PDF processing with memory management"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE):
        self.chunk_size = chunk_size
    
    def process_large_pdf(self, pdf_file: Union[str, bytes], operation_func) -> bytes:
        """
        Process large PDFs in chunks to avoid memory issues
        """
        doc = fitz.open(pdf_file)
        total_pages = doc.page_count
        result_docs = []
        
        try:
            for i in range(0, total_pages, self.chunk_size):
                chunk_end = min(i + self.chunk_size, total_pages)
                chunk_doc = fitz.open()
                
                # Process chunk
                for page_num in range(i, chunk_end):
                    page = doc[page_num]
                    new_page = chunk_doc.new_page(width=page.rect.width, height=page.rect.height)
                    new_page.show_pdf_page(page.rect, doc, page_num)
                    
                    # Apply operation
                    operation_func(new_page, page_num + 1)
                
                result_docs.append(chunk_doc)
                
                # Memory cleanup
                if i % 50 == 0:
                    gc.collect()
            
            # Combine all chunks
            final_doc = fitz.open()
            for chunk_doc in result_docs:
                for page in chunk_doc:
                    final_doc.insert_pdf(chunk_doc, from_page=page.number, to_page=page.number)
                chunk_doc.close()
            
            result_bytes = BytesIO(final_doc.save())
            return result_bytes.getvalue()
            
        finally:
            doc.close()
            final_doc.close()
            for chunk_doc in result_docs:
                chunk_doc.close()


def validate_file_size(pdf_file: Union[str, bytes]) -> bool:
    """
    Validate file size before processing
    """
    if isinstance(pdf_file, str):
        file_size = os.path.getsize(pdf_file)
    else:
        file_size = len(pdf_file)
    
    if file_size > MAX_FILE_SIZE:
        raise PDFProcessingError(
            f"File size ({file_size/1024/1024:.1f}MB) exceeds maximum allowed size ({MAX_FILE_SIZE/1024/1024:.1f}MB)",
            "FILE_TOO_LARGE"
        )
    
    return True


def validate_page_range(from_page: int, to_page: int, total_pages: int) -> Dict[str, Any]:
    """
    Validate page range input
    """
    errors = []
    
    # Check if values are valid numbers
    if not isinstance(from_page, int) or not isinstance(to_page, int):
        errors.append("Page numbers must be valid integers")
        return {"valid": False, "errors": errors}
    
    # Check if pages are within document range
    if from_page < 1 or from_page > total_pages:
        errors.append(f"From page must be between 1 and {total_pages}")
    
    if to_page < 1 or to_page > total_pages:
        errors.append(f"To page must be between 1 and {total_pages}")
    
    # Check if range is logical
    if from_page > to_page:
        errors.append("From page must be less than or equal to To page")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def get_text_position(page_rect: fitz.Rect, position: str) -> Tuple[float, float]:
    """
    Calculate text position based on page dimensions and desired position
    """
    width = page_rect.width
    height = page_rect.height
    margin = 50  # Margin from edges
    
    positions = {
        "bottom-center": (width/2 - 50, height - margin),
        "bottom-left": (margin, height - margin),
        "bottom-right": (width - 150, height - margin),
        "top-center": (width/2 - 50, margin),
        "top-left": (margin, margin),
        "top-right": (width - 150, margin),
        "center": (width/2 - 50, height/2)
    }
    
    return positions.get(position, positions["bottom-center"])


def add_page_numbers_enhanced(pdf_file: Union[str, bytes], 
                            format_string: str = "Page {n}",
                            position: str = "bottom-center",
                            font_size: int = 12,
                            color: Tuple[int, int, int] = (0, 0, 0),
                            start_page: int = 1) -> bytes:
    """
    Enhanced page numbering with large file support
    """
    def add_number_to_page(page, page_num):
        """Add page number to individual page"""
        if page_num >= start_page:
            page_text = format_string.format(n=page_num)
            text_rect = get_text_position(page.rect, position)
            
            # Create text annotation
            page.insert_text(
                text_rect, 
                page_text, 
                fontsize=font_size, 
                color=color
            )
    
    # Validate file size
    validate_file_size(pdf_file)
    
    # Get document info
    doc = fitz.open(pdf_file)
    total_pages = doc.page_count
    doc.close()
    
    # Use large file processor if needed
    if isinstance(pdf_file, str) and os.path.getsize(pdf_file) > 50 * 1024 * 1024:  # 50MB threshold
        processor = LargePDFProcessor()
        return processor.process_large_pdf(pdf_file, add_number_to_page)
    else:
        # Standard processing for smaller files
        doc = fitz.open(pdf_file)
        result_doc = fitz.open()
        
        try:
            for page_num in range(total_pages):
                page = doc[page_num]
                new_page = result_doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.show_pdf_page(page.rect, doc, page_num)
                add_number_to_page(new_page, page_num + 1)
            
            result_bytes = BytesIO(result_doc.save())
            return result_bytes.getvalue()
            
        finally:
            doc.close()
            result_doc.close()


def split_pdf_enhanced(pdf_file: Union[str, bytes], 
                      from_page: int, 
                      to_page: int) -> bytes:
    """
    Enhanced PDF split with validation
    """
    # Validate file size
    validate_file_size(pdf_file)
    
    # Get document info
    doc = fitz.open(pdf_file)
    total_pages = doc.page_count
    
    # Validate page range
    validation = validate_page_range(from_page, to_page, total_pages)
    if not validation["valid"]:
        raise PDFProcessingError(
            f"Invalid page range: {', '.join(validation['errors'])}",
            "INVALID_PAGE_RANGE"
        )
    
    try:
        result_doc = fitz.open()
        
        # Copy pages in the specified range
        for page_num in range(from_page - 1, to_page):  # Convert to 0-based
            page = doc[page_num]
            new_page = result_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.show_pdf_page(page.rect, doc, page_num)
        
        result_bytes = BytesIO(result_doc.save())
        return result_bytes.getvalue()
        
    finally:
        doc.close()
        result_doc.close()


def extract_pages_enhanced(pdf_file: Union[str, bytes], 
                         page_numbers: List[int]) -> bytes:
    """
    Enhanced page extraction with validation
    """
    # Validate file size
    validate_file_size(pdf_file)
    
    # Get document info
    doc = fitz.open(pdf_file)
    total_pages = doc.page_count
    
    # Validate page numbers
    invalid_pages = [p for p in page_numbers if p < 1 or p > total_pages]
    if invalid_pages:
        raise PDFProcessingError(
            f"Invalid page numbers: {invalid_pages}. Valid range: 1-{total_pages}",
            "INVALID_PAGE_NUMBERS"
        )
    
    try:
        result_doc = fitz.open()
        
        # Extract specified pages
        for page_num in sorted(page_numbers):
            page = doc[page_num - 1]  # Convert to 0-based
            new_page = result_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.show_pdf_page(page.rect, doc, page_num)
        
        result_bytes = BytesIO(result_doc.save())
        return result_bytes.getvalue()
        
    finally:
        doc.close()
        result_doc.close()


def rotate_pdf_enhanced(pdf_file: Union[str, bytes], 
                       angle: int = 90,
                       page_range: str = "all") -> bytes:
    """
    Enhanced PDF rotation with validation
    """
    # Validate file size
    validate_file_size(pdf_file)
    
    # Validate angle
    valid_angles = [0, 90, 180, 270, -90, -180, -270]
    if angle not in valid_angles:
        raise PDFProcessingError(
            f"Invalid rotation angle: {angle}. Valid angles: {valid_angles}",
            "INVALID_ROTATION_ANGLE"
        )
    
    doc = fitz.open(pdf_file)
    result_doc = fitz.open()
    
    try:
        total_pages = doc.page_count
        
        for page_num in range(total_pages):
            page = doc[page_num]
            
            # Apply rotation if page is in range
            if page_range == "all" or (page_range.isdigit() and int(page_range) == page_num + 1):
                rotated_page = result_doc.new_page(width=page.rect.width, height=page.rect.height)
                rotated_page.show_pdf_page(page.rect, doc, page_num, rotate=angle)
            else:
                # Copy without rotation
                new_page = result_doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.show_pdf_page(page.rect, doc, page_num)
        
        result_bytes = BytesIO(result_doc.save())
        return result_bytes.getvalue()
        
    finally:
        doc.close()
        result_doc.close()


def pdf_to_images_enhanced(pdf_file: Union[str, bytes], 
                          dpi: int = 150,
                          format: str = "PNG") -> List[bytes]:
    """
    Enhanced PDF to image conversion with progress tracking
    """
    # Validate file size
    validate_file_size(pdf_file)
    
    # Validate DPI
    if dpi < 72 or dpi > 600:
        raise PDFProcessingError(
            f"Invalid DPI: {dpi}. Valid range: 72-600",
            "INVALID_DPI"
        )
    
    # Validate format
    valid_formats = ["PNG", "JPEG", "WEBP"]
    if format.upper() not in valid_formats:
        raise PDFProcessingError(
            f"Invalid format: {format}. Valid formats: {valid_formats}",
            "INVALID_FORMAT"
        )
    
    doc = fitz.open(pdf_file)
    images = []
    
    try:
        total_pages = doc.page_count
        
        for page_num in range(total_pages):
            page = doc[page_num]
            
            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            
            # Convert to bytes
            img_data = pix.tobytes(format.lower())
            images.append(img_data)
            
            # Memory cleanup
            del pix
            if page_num % 10 == 0:
                gc.collect()
        
        return images
        
    finally:
        doc.close()


def extract_images_enhanced(pdf_file: Union[str, bytes]) -> List[Tuple[bytes, str]]:
    """
    Enhanced image extraction from PDF with metadata
    """
    # Validate file size
    validate_file_size(pdf_file)
    
    doc = fitz.open(pdf_file)
    extracted_images = []
    
    try:
        total_pages = doc.page_count
        
        for page_num in range(total_pages):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                # Get image data
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                if pix.n - pix.alpha < 4:  # Exclude CMYK images
                    img_data = pix.tobytes("png")
                    extracted_images.append((img_data, f"page_{page_num+1}_image_{img_index+1}.png"))
                
                # Memory cleanup
                pix = None
                if img_index % 5 == 0:
                    gc.collect()
        
        return extracted_images
        
    finally:
        doc.close()


def merge_pdfs_enhanced(pdf_files: List[Union[str, bytes]], 
                       output_path: str = None) -> bytes:
    """
    Enhanced PDF merge with validation and progress tracking
    """
    # Validate file sizes
    for i, pdf_file in enumerate(pdf_files):
        validate_file_size(pdf_file)
    
    result_doc = fitz.open()
    
    try:
        for i, pdf_file in enumerate(pdf_files):
            doc = fitz.open(pdf_file)
            
            for page in doc:
                new_page = result_doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.show_pdf_page(page.rect, doc, page.number)
            
            doc.close()
            
            # Memory cleanup
            if i % 5 == 0:
                gc.collect()
        
        result_bytes = BytesIO(result_doc.save())
        return result_bytes.getvalue()
        
    finally:
        result_doc.close()


# Utility functions
def get_pdf_info(pdf_file: Union[str, bytes]) -> Dict[str, Any]:
    """
    Get comprehensive PDF information
    """
    try:
        validate_file_size(pdf_file)
        doc = fitz.open(pdf_file)
        
        info = {
            "page_count": doc.page_count,
            "metadata": doc.metadata,
            "file_size": len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file),
            "is_encrypted": doc.needs_pass,
            "has_forms": len(doc.get_widgets()) > 0
        }
        
        doc.close()
        return info
        
    except Exception as e:
        raise PDFProcessingError(f"Error getting PDF info: {str(e)}", "INFO_ERROR")


def safe_pdf_operation(operation_func, *args, **kwargs):
    """
    Wrapper for safe PDF operations with proper error handling
    """
    try:
        return operation_func(*args, **kwargs)
    except fitz.FileDataError as e:
        raise PDFProcessingError("Invalid PDF file", "INVALID_PDF", str(e))
    except MemoryError as e:
        raise PDFProcessingError("Insufficient memory for large file", "MEMORY_ERROR", str(e))
    except PDFProcessingError:
        raise  # Re-raise our custom exceptions
    except Exception as e:
        raise PDFProcessingError("Unexpected error during processing", "UNKNOWN_ERROR", str(e))
