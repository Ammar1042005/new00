"""
Categorized PDF Tools - Organized by functionality
"""

import fitz  # PyMuPDF
import io
import os
import gc
from PIL import Image
from typing import Union, List, Tuple, Dict, Any

# =============================================================================
# PDF INFORMATION & VALIDATION FUNCTIONS
# =============================================================================

def get_pdf_info(pdf_file: Union[str, bytes]) -> Dict[str, Any]:
    """
    Get comprehensive PDF information
    
    Args:
        pdf_file: PDF file path or bytes
        
    Returns:
        Dictionary with PDF information
    """
    try:
        doc = fitz.open(pdf_file)
        
        info = {
            'page_count': doc.page_count,
            'is_encrypted': doc.is_encrypted,
            'metadata': doc.metadata,
            'file_size': len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file),
            'has_images': False,
            'has_text': False,
            'creation_date': None,
            'modification_date': None
        }
        
        # Check for images and text
        for page in doc:
            if page.get_images():
                info['has_images'] = True
            if page.get_text():
                info['has_text'] = True
        
        # Get dates
        if info['metadata']:
            info['creation_date'] = info['metadata'].get('creationDate')
            info['modification_date'] = info['metadata'].get('modDate')
        
        doc.close()
        return info
        
    except Exception as e:
        raise Exception(f"Error getting PDF info: {str(e)}")


def validate_file_size(pdf_file: Union[str, bytes], max_size: int = 100 * 1024 * 1024) -> bool:
    """
    Validate PDF file size
    
    Args:
        pdf_file: PDF file path or bytes
        max_size: Maximum allowed size in bytes (default: 100MB)
        
    Returns:
        True if file size is valid
        
    Raises:
        Exception: If file is too large
    """
    file_size = len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file)
    
    if file_size > max_size:
        raise Exception(f"File size ({file_size/1024/1024:.1f}MB) exceeds maximum allowed size ({max_size/1024/1024:.1f}MB)")
    
    return True


def validate_page_range(from_page: int, to_page: int, total_pages: int) -> Dict[str, Any]:
    """
    Validate page range
    
    Args:
        from_page: Starting page number
        to_page: Ending page number
        total_pages: Total pages in PDF
        
    Returns:
        Validation result with errors if any
    """
    errors = []
    
    if from_page < 1 or from_page > total_pages:
        errors.append(f"From page must be between 1 and {total_pages}")
    
    if to_page < 1 or to_page > total_pages:
        errors.append(f"To page must be between 1 and {total_pages}")
    
    if from_page > to_page:
        errors.append("From page must be less than or equal to To page")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


# =============================================================================
# PDF MANIPULATION FUNCTIONS
# =============================================================================

def merge_pdfs_categorized(pdf_files: List[Union[str, bytes]], output_path: str = None) -> bytes:
    """
    Merge multiple PDFs into one
    
    Args:
        pdf_files: List of PDF file paths or bytes
        output_path: Optional output file path
        
    Returns:
        Merged PDF bytes
    """
    if len(pdf_files) < 2:
        raise Exception("Please provide at least 2 PDF files to merge")
    
    try:
        merged_doc = fitz.open()
        
        for pdf_file in pdf_files:
            doc = fitz.open(pdf_file)
            merged_doc.insert_pdf(doc)
            doc.close()
        
        result = merged_doc.save(garbage=4, deflate=True)
        merged_doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error merging PDFs: {str(e)}")


def split_pdf_categorized(pdf_file: Union[str, bytes], from_page: int, to_page: int, output_path: str = None) -> bytes:
    """
    Split PDF into page range
    
    Args:
        pdf_file: PDF file path or bytes
        from_page: Starting page number (1-based)
        to_page: Ending page number (1-based)
        output_path: Optional output file path
        
    Returns:
        Split PDF bytes
    """
    try:
        doc = fitz.open(pdf_file)
        
        # Validate page range
        if from_page < 1 or to_page > doc.page_count or from_page > to_page:
            raise Exception(f"Invalid page range: {from_page}-{to_page} for PDF with {doc.page_count} pages")
        
        # Create new document with selected pages
        new_doc = fitz.open()
        
        for page_num in range(from_page - 1, to_page):
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
        result = new_doc.save(garbage=4, deflate=True)
        new_doc.close()
        doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error splitting PDF: {str(e)}")


def extract_pages_categorized(pdf_file: Union[str, bytes], page_numbers: List[int], output_path: str = None) -> bytes:
    """
    Extract specific pages from PDF
    
    Args:
        pdf_file: PDF file path or bytes
        page_numbers: List of page numbers to extract (1-based)
        output_path: Optional output file path
        
    Returns:
        Extracted PDF bytes
    """
    try:
        doc = fitz.open(pdf_file)
        
        # Validate page numbers
        max_page = doc.page_count
        valid_pages = []
        for page_num in page_numbers:
            if 1 <= page_num <= max_page:
                valid_pages.append(page_num - 1)  # Convert to 0-based
        
        if not valid_pages:
            raise Exception("No valid pages to extract")
        
        # Create new document with selected pages
        new_doc = fitz.open()
        
        for page_num in sorted(valid_pages):
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
        result = new_doc.save(garbage=4, deflate=True)
        new_doc.close()
        doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error extracting pages: {str(e)}")


def rotate_pdf_categorized(pdf_file: Union[str, bytes], angle: int = 90, page_range: str = "all", output_path: str = None) -> bytes:
    """
    Rotate PDF pages
    
    Args:
        pdf_file: PDF file path or bytes
        angle: Rotation angle (90, 180, 270, -90, -180, -270)
        page_range: Page range ("all" or specific page number)
        output_path: Optional output file path
        
    Returns:
        Rotated PDF bytes
    """
    try:
        doc = fitz.open(pdf_file)
        
        # Validate angle
        valid_angles = [90, 180, 270, -90, -180, -270]
        if angle not in valid_angles:
            raise Exception(f"Invalid rotation angle: {angle}. Valid angles: {valid_angles}")
        
        # Rotate pages
        if page_range == "all":
            for page in doc:
                page.set_rotation(angle)
        else:
            try:
                page_num = int(page_range) - 1
                if 0 <= page_num < doc.page_count:
                    doc[page_num].set_rotation(angle)
                else:
                    raise Exception(f"Page {page_num + 1} not found")
            except ValueError:
                raise Exception("Invalid page range")
        
        result = doc.save(garbage=4, deflate=True)
        doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error rotating PDF: {str(e)}")


# =============================================================================
# PDF CONTENT MODIFICATION FUNCTIONS
# =============================================================================

def add_page_numbers_categorized(pdf_file: Union[str, bytes], 
                               format_string: str = "Page {n}",
                               position: str = "bottom-center",
                               font_size: int = 12,
                               start_page: int = 1,
                               output_path: str = None) -> bytes:
    """
    Add page numbers to PDF
    
    Args:
        pdf_file: PDF file path or bytes
        format_string: Page number format (e.g., "Page {n}", "{n}", "Page {n} of {total}")
        position: Position of page numbers
        font_size: Font size for page numbers
        start_page: Starting page number
        output_path: Optional output file path
        
    Returns:
        PDF bytes with page numbers
    """
    try:
        doc = fitz.open(pdf_file)
        
        # Position coordinates
        positions = {
            "bottom-center": (fitz.Point(306, 780)),
            "bottom-left": (fitz.Point(72, 780)),
            "bottom-right": (fitz.Point(540, 780)),
            "top-center": (fitz.Point(306, 12)),
            "top-left": (fitz.Point(72, 12)),
            "top-right": (fitz.Point(540, 12))
        }
        
        if position not in positions:
            position = "bottom-center"
        
        point = positions[position]
        
        # Add page numbers
        for page_num, page in enumerate(doc):
            current_page = start_page + page_num
            
            if "{total}" in format_string:
                page_text = format_string.format(n=current_page, total=doc.page_count)
            else:
                page_text = format_string.format(n=current_page)
            
            # Create text rectangle
            rect = fitz.Rect(point.x - 100, point.y - 10, point.x + 100, point.y + 10)
            
            # Add text
            page.insert_text(point, page_text, fontsize=font_size, color=(0, 0, 0))
        
        result = doc.save(garbage=4, deflate=True)
        doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error adding page numbers: {str(e)}")


def add_watermark_categorized(pdf_file: Union[str, bytes], 
                             watermark_text: str,
                             position: str = "center",
                             opacity: float = 0.3,
                             rotation: int = 45,
                             font_size: int = 48,
                             output_path: str = None) -> bytes:
    """
    Add watermark to PDF
    
    Args:
        pdf_file: PDF file path or bytes
        watermark_text: Watermark text
        position: Watermark position
        opacity: Text opacity (0.0 to 1.0)
        rotation: Text rotation angle
        font_size: Font size for watermark
        output_path: Optional output file path
        
    Returns:
        PDF bytes with watermark
    """
    try:
        doc = fitz.open(pdf_file)
        
        # Position coordinates
        positions = {
            "center": (fitz.Point(306, 396)),
            "top-left": (fitz.Point(100, 100)),
            "top-right": (fitz.Point(512, 100)),
            "bottom-left": (fitz.Point(100, 692)),
            "bottom-right": (fitz.Point(512, 692))
        }
        
        if position not in positions:
            position = "center"
        
        point = positions[position]
        
        # Add watermark to each page
        for page in doc:
            # Create watermark with rotation
            page.insert_text(
                point, 
                watermark_text, 
                fontsize=font_size,
                color=(0.5, 0.5, 0.5),
                rotate=rotation
            )
        
        result = doc.save(garbage=4, deflate=True)
        doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error adding watermark: {str(e)}")


# =============================================================================
# PDF CONVERSION FUNCTIONS
# =============================================================================

def pdf_to_images_categorized(pdf_file: Union[str, bytes], 
                             dpi: int = 150,
                             format_type: str = "PNG",
                             output_folder: str = None) -> List[bytes]:
    """
    Convert PDF pages to images
    
    Args:
        pdf_file: PDF file path or bytes
        dpi: Output image DPI
        format_type: Image format (PNG, JPEG, WEBP)
        output_folder: Optional folder to save images
        
    Returns:
        List of image bytes
    """
    try:
        doc = fitz.open(pdf_file)
        images = []
        
        # Validate format
        valid_formats = ["PNG", "JPEG", "WEBP"]
        if format_type not in valid_formats:
            format_type = "PNG"
        
        # Convert each page
        for page_num, page in enumerate(doc):
            # Render page as image
            matrix = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=matrix)
            
            # Convert to bytes
            img_data = pix.tobytes(format_type.lower())
            images.append(img_data)
            
            # Save to folder if specified
            if output_folder:
                os.makedirs(output_folder, exist_ok=True)
                output_path = os.path.join(output_folder, f"page_{page_num + 1}.{format_type.lower()}")
                with open(output_path, 'wb') as f:
                    f.write(img_data)
            
            pix = None
        
        doc.close()
        return images
        
    except Exception as e:
        raise Exception(f"Error converting PDF to images: {str(e)}")


def extract_images_categorized(pdf_file: Union[str, bytes], 
                             output_folder: str = None) -> List[Tuple[bytes, str]]:
    """
    Extract images from PDF
    
    Args:
        pdf_file: PDF file path or bytes
        output_folder: Optional folder to save images
        
    Returns:
        List of (image_bytes, filename) tuples
    """
    try:
        doc = fitz.open(pdf_file)
        extracted_images = []
        
        for page_num, page in enumerate(doc):
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    # Skip CMYK images
                    if pix.n - pix.alpha >= 4:
                        pix = None
                        continue
                    
                    # Convert to bytes
                    img_data = pix.tobytes("png")
                    filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                    
                    extracted_images.append((img_data, filename))
                    
                    # Save to folder if specified
                    if output_folder:
                        os.makedirs(output_folder, exist_ok=True)
                        output_path = os.path.join(output_folder, filename)
                        with open(output_path, 'wb') as f:
                            f.write(img_data)
                    
                    pix = None
                    
                except Exception as e:
                    print(f"Error extracting image {img_index} from page {page_num}: {e}")
                    continue
        
        doc.close()
        return extracted_images
        
    except Exception as e:
        raise Exception(f"Error extracting images from PDF: {str(e)}")


# =============================================================================
# PDF COMPRESSION FUNCTIONS
# =============================================================================

def compress_pdf_categorized(pdf_file: Union[str, bytes], 
                            method: str = "standard",
                            output_path: str = None) -> bytes:
    """
    Compress PDF file
    
    Args:
        pdf_file: PDF file path or bytes
        method: Compression method ("standard", "aggressive", "image")
        output_path: Optional output file path
        
    Returns:
        Compressed PDF bytes
    """
    try:
        doc = fitz.open(pdf_file)
        original_size = len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file)
        
        if method == "standard":
            # Standard compression - remove metadata and optimize
            doc.set_metadata({})
            result = doc.save(garbage=4, deflate=True, deflate_images=True)
        
        elif method == "aggressive":
            # Aggressive compression - convert to images
            new_doc = fitz.open()
            
            for page in doc:
                # Render page as image at lower DPI
                pix = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))
                
                # Convert to PIL Image and compress
                img_data = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_data))
                
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # Save as JPEG with low quality
                img_buffer = io.BytesIO()
                pil_image.save(img_buffer, format='JPEG', quality=50, optimize=True)
                
                # Create new page
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                img_rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
                new_page.insert_image(img_rect, stream=img_buffer.getvalue())
                
                pix = None
                pil_image = None
                img_buffer = None
            
            result = new_doc.save(garbage=4, deflate=True)
            new_doc.close()
        
        else:
            # Default to standard
            doc.set_metadata({})
            result = doc.save(garbage=4, deflate=True)
        
        doc.close()
        
        # Verify compression worked
        compressed_size = len(result)
        if compressed_size >= original_size:
            raise Exception("Compression did not reduce file size")
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error compressing PDF: {str(e)}")


# =============================================================================
# PDF TEXT PROCESSING FUNCTIONS
# =============================================================================

def extract_text_categorized(pdf_file: Union[str, bytes], 
                           page_numbers: List[int] = None) -> str:
    """
    Extract text from PDF
    
    Args:
        pdf_file: PDF file path or bytes
        page_numbers: Optional list of page numbers to extract from
        
    Returns:
        Extracted text as string
    """
    try:
        doc = fitz.open(pdf_file)
        text = ""
        
        if page_numbers:
            # Extract from specific pages
            for page_num in page_numbers:
                if 1 <= page_num <= doc.page_count:
                    page = doc[page_num - 1]
                    text += page.get_text() + "\n"
        else:
            # Extract from all pages
            for page in doc:
                text += page.get_text() + "\n"
        
        doc.close()
        return text.strip()
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def search_text_categorized(pdf_file: Union[str, bytes], 
                          search_term: str,
                          case_sensitive: bool = False) -> List[Dict[str, Any]]:
    """
    Search for text in PDF
    
    Args:
        pdf_file: PDF file path or bytes
        search_term: Text to search for
        case_sensitive: Whether search is case sensitive
        
    Returns:
        List of search results with page numbers and positions
    """
    try:
        doc = fitz.open(pdf_file)
        results = []
        
        if not case_sensitive:
            search_term = search_term.lower()
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            
            if not case_sensitive:
                search_text = text.lower()
            else:
                search_text = text
            
            if search_term in search_text:
                # Find all occurrences
                start = 0
                while True:
                    pos = search_text.find(search_term, start)
                    if pos == -1:
                        break
                    
                    results.append({
                        "page": page_num + 1,
                        "position": pos,
                        "context": text[max(0, pos-50):pos+len(search_term)+50]
                    })
                    start = pos + 1
        
        doc.close()
        return results
        
    except Exception as e:
        raise Exception(f"Error searching text in PDF: {str(e)}")


# =============================================================================
# PDF SECURITY FUNCTIONS
# =============================================================================

def encrypt_pdf_categorized(pdf_file: Union[str, bytes], 
                          password: str,
                          owner_password: str = None,
                          permissions: Dict[str, bool] = None,
                          output_path: str = None) -> bytes:
    """
    Encrypt PDF with password
    
    Args:
        pdf_file: PDF file path or bytes
        password: User password for opening PDF
        owner_password: Owner password for permissions (optional)
        permissions: Dictionary of permissions (print, copy, modify, etc.)
        output_path: Optional output file path
        
    Returns:
        Encrypted PDF bytes
    """
    try:
        doc = fitz.open(pdf_file)
        
        # Default permissions
        if permissions is None:
            permissions = {
                "print": True,
                "copy": True,
                "modify": True,
                "annotate": True
            }
        
        # Encrypt document
        encrypt_meth = fitz.PDF_ENCRYPT_AES_256
        doc.save(
            output_path or "temp_encrypted.pdf",
            encryption=encrypt_meth,
            user_pw=password,
            owner_pw=owner_password or password,
            permissions=permissions
        )
        
        # Read encrypted file
        if output_path:
            with open(output_path, 'rb') as f:
                result = f.read()
        else:
            with open("temp_encrypted.pdf", 'rb') as f:
                result = f.read()
            os.remove("temp_encrypted.pdf")
        
        doc.close()
        return result
        
    except Exception as e:
        raise Exception(f"Error encrypting PDF: {str(e)}")


def decrypt_pdf_categorized(pdf_file: Union[str, bytes], 
                          password: str,
                          output_path: str = None) -> bytes:
    """
    Decrypt PDF
    
    Args:
        pdf_file: PDF file path or bytes
        password: Password to decrypt PDF
        output_path: Optional output file path
        
    Returns:
        Decrypted PDF bytes
    """
    try:
        doc = fitz.open(pdf_file)
        
        if doc.is_encrypted:
            if not doc.authenticate(password):
                raise Exception("Incorrect password")
        
        # Save without encryption
        result = doc.save(garbage=4, deflate=True)
        doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error decrypting PDF: {str(e)}")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_blank_pdf_categorized(page_count: int = 1,
                                page_size: str = "A4",
                                output_path: str = None) -> bytes:
    """
    Create blank PDF
    
    Args:
        page_count: Number of pages
        page_size: Page size ("A4", "Letter", "Legal")
        output_path: Optional output file path
        
    Returns:
        Blank PDF bytes
    """
    try:
        # Page dimensions (in points)
        sizes = {
            "A4": (595, 842),
            "Letter": (612, 792),
            "Legal": (612, 1008)
        }
        
        if page_size not in sizes:
            page_size = "A4"
        
        width, height = sizes[page_size]
        
        doc = fitz.open()
        
        for _ in range(page_count):
            doc.new_page(width=width, height=height)
        
        result = doc.save(garbage=4, deflate=True)
        doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error creating blank PDF: {str(e)}")


def compare_pdfs_categorized(pdf1: Union[str, bytes], 
                           pdf2: Union[str, bytes]) -> Dict[str, Any]:
    """
    Compare two PDFs
    
    Args:
        pdf1: First PDF file path or bytes
        pdf2: Second PDF file path or bytes
        
    Returns:
        Comparison result with differences
    """
    try:
        doc1 = fitz.open(pdf1)
        doc2 = fitz.open(pdf2)
        
        comparison = {
            "identical": True,
            "differences": []
        }
        
        # Compare page count
        if doc1.page_count != doc2.page_count:
            comparison["identical"] = False
            comparison["differences"].append(f"Page count: {doc1.page_count} vs {doc2.page_count}")
        
        # Compare each page
        min_pages = min(doc1.page_count, doc2.page_count)
        for page_num in range(min_pages):
            page1_text = doc1[page_num].get_text()
            page2_text = doc2[page_num].get_text()
            
            if page1_text != page2_text:
                comparison["identical"] = False
                comparison["differences"].append(f"Page {page_num + 1}: Text content differs")
        
        # Compare file sizes
        size1 = len(pdf1) if isinstance(pdf1, bytes) else os.path.getsize(pdf1)
        size2 = len(pdf2) if isinstance(pdf2, bytes) else os.path.getsize(pdf2)
        
        if size1 != size2:
            comparison["identical"] = False
            comparison["differences"].append(f"File size: {size1} vs {size2} bytes")
        
        doc1.close()
        doc2.close()
        
        return comparison
        
    except Exception as e:
        raise Exception(f"Error comparing PDFs: {str(e)}")


# =============================================================================
# MAIN FUNCTION - DEMONSTRATION
# =============================================================================

def demonstrate_categorized_functions():
    """
    Demonstrate all categorized PDF functions
    """
    print("Categorized PDF Tools - Function Demonstration")
    print("=" * 60)
    
    # Create a sample PDF for demonstration
    sample_pdf = "sample_demo.pdf"
    create_blank_pdf_categorized(3, "A4", sample_pdf)
    
    print(f"Created sample PDF: {sample_pdf}")
    
    # Demonstrate each category
    print("\n1. PDF INFORMATION & VALIDATION")
    info = get_pdf_info(sample_pdf)
    print(f"   PDF Info: {info['page_count']} pages, {info['file_size']} bytes")
    
    print("\n2. PDF MANIPULATION")
    # Add some content first
    try:
        from final_working_compression import compress_pdf_simple
        print("   Compression function available")
    except:
        print("   Compression function not available")
    
    print("\n3. PDF CONVERSION")
    images = pdf_to_images_categorized(sample_pdf, 72, "PNG")
    print(f"   Converted to {len(images)} images")
    
    print("\n4. PDF TEXT PROCESSING")
    text = extract_text_categorized(sample_pdf)
    print(f"   Extracted text: {len(text)} characters")
    
    print("\n5. PDF SECURITY")
    print("   Security functions available (encrypt, decrypt)")
    
    print("\n6. UTILITY FUNCTIONS")
    comparison = compare_pdfs_categorized(sample_pdf, sample_pdf)
    print(f"   Self-comparison: {'Identical' if comparison['identical'] else 'Different'}")
    
    # Clean up
    if os.path.exists(sample_pdf):
        os.remove(sample_pdf)
    
    print("\nDemonstration completed!")


if __name__ == "__main__":
    demonstrate_categorized_functions()
