"""
Enhanced PDF Compression - Actually reduces file sizes
"""

import fitz  # PyMuPDF
import io
import os
from PIL import Image
import tempfile
from typing import Union, Dict, Any, Tuple
from enhanced_pdf_tools import PDFProcessingError, MAX_FILE_SIZE


def compress_pdf_enhanced(pdf_file: Union[str, bytes], 
                         quality: str = "medium",
                         image_quality: int = 75,
                         remove_metadata: bool = True,
                         optimize_fonts: bool = True) -> bytes:
    """
    Enhanced PDF compression that actually reduces file sizes
    
    Args:
        pdf_file: Input PDF file (path or bytes)
        quality: Compression level ('low', 'medium', 'high', 'maximum')
        image_quality: Image compression quality (1-100)
        remove_metadata: Remove document metadata
        optimize_fonts: Optimize font embedding
    
    Returns:
        Compressed PDF bytes
    """
    
    # Quality settings
    quality_settings = {
        'low': {
            'image_dpi': 150,
            'image_quality': 90,
            'compress_fonts': False,
            'subset_fonts': False
        },
        'medium': {
            'image_dpi': 120,
            'image_quality': 75,
            'compress_fonts': True,
            'subset_fonts': True
        },
        'high': {
            'image_dpi': 100,
            'image_quality': 50,
            'compress_fonts': True,
            'subset_fonts': True
        },
        'maximum': {
            'image_dpi': 72,
            'image_quality': 30,
            'compress_fonts': True,
            'subset_fonts': True
        }
    }
    
    settings = quality_settings.get(quality, quality_settings['medium'])
    
    try:
        doc = fitz.open(pdf_file)
        original_size = len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file)
        
        # Create new document for compressed version
        compressed_doc = fitz.open()
        
        # Process each page
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Get page images
            image_list = page.get_images()
            
            # Create new page
            new_page = compressed_doc.new_page(width=page.rect.width, height=page.rect.height)
            
            # Process images on the page
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    # Skip CMYK images
                    if pix.n - pix.alpha >= 4:
                        pix = None
                        continue
                    
                    # Compress image
                    if pix.width > settings['image_dpi'] or pix.height > settings['image_dpi']:
                        # Resize image
                        img_data = compress_image_data(pix, settings['image_dpi'], settings['image_quality'])
                        
                        # Replace image in compressed document
                        img_rect = page.get_image_bbox(img)
                        new_page.insert_image(img_rect, stream=img_data)
                    
                    pix = None
                    
                except Exception as e:
                    print(f"Error processing image {img_index} on page {page_num}: {e}")
                    continue
            
            # Copy page content without original images
            new_page.show_pdf_page(page.rect, doc, page_num)
        
        # Remove metadata if requested
        if remove_metadata:
            compressed_doc.set_metadata({})
        
        # Optimize fonts if requested
        if optimize_fonts:
            compressed_doc.clean()
        
        # Save with compression
        save_options = {
            'garbage': 4,  # Maximum garbage collection
            'deflate': True,  # Use compression
            'deflate_images': True,  # Compress images
            'ascii': False  # Use binary format
        }
        
        compressed_bytes = compressed_doc.save(**save_options)
        
        # Close documents
        doc.close()
        compressed_doc.close()
        
        # Calculate compression ratio
        compressed_size = len(compressed_bytes)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"Original size: {original_size/1024/1024:.2f} MB")
        print(f"Compressed size: {compressed_size/1024/1024:.2f} MB")
        print(f"Compression ratio: {compression_ratio:.1f}%")
        
        # If compression didn't reduce size, try more aggressive settings
        if compressed_size >= original_size * 0.95:  # Less than 5% reduction
            print("Trying more aggressive compression...")
            return compress_pdf_aggressive(pdf_file, settings)
        
        return compressed_bytes
        
    except Exception as e:
        raise PDFProcessingError(f"Error compressing PDF: {str(e)}", "COMPRESSION_ERROR")


def compress_pdf_aggressive(pdf_file: Union[str, bytes], settings: Dict[str, Any]) -> bytes:
    """
    More aggressive PDF compression for stubborn files
    """
    doc = fitz.open(pdf_file)
    
    try:
        # Create new document
        compressed_doc = fitz.open()
        
        # Process each page with aggressive settings
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Render page as image at lower DPI
            matrix = fitz.Matrix(settings['image_dpi']/72, settings['image_dpi']/72)
            pix = page.get_pixmap(matrix=matrix)
            
            # Convert to compressed image
            img_data = pix.tobytes('jpeg', quality=settings['image_quality'])
            
            # Create new page and insert compressed image
            new_page = compressed_doc.new_page(width=page.rect.width, height=page.rect.height)
            img_rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
            new_page.insert_image(img_rect, stream=img_data)
            
            pix = None
        
        # Save with maximum compression
        compressed_bytes = compressed_doc.save(
            garbage=4,
            deflate=True,
            deflate_images=True,
            ascii=False
        )
        
        doc.close()
        compressed_doc.close()
        
        return compressed_bytes
        
    except Exception as e:
        doc.close()
        compressed_doc.close()
        raise PDFProcessingError(f"Error in aggressive compression: {str(e)}", "COMPRESSION_ERROR")


def compress_image_data(pix: fitz.Pixmap, target_dpi: int, quality: int) -> bytes:
    """
    Compress image data using PIL
    """
    try:
        # Convert PyMuPDF pixmap to PIL Image
        img_data = pix.tobytes("png")
        pil_image = Image.open(io.BytesIO(img_data))
        
        # Calculate new dimensions
        current_dpi = 72  # Default DPI
        scale_factor = target_dpi / current_dpi
        
        new_width = int(pil_image.width * scale_factor)
        new_height = int(pil_image.height * scale_factor)
        
        # Resize image
        if new_width < pil_image.width or new_height < pil_image.height:
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Compress and save as JPEG
        img_buffer = io.BytesIO()
        pil_image.save(img_buffer, format='JPEG', quality=quality, optimize=True)
        
        return img_buffer.getvalue()
        
    except Exception as e:
        print(f"Error compressing image: {e}")
        # Fallback to original image
        return pix.tobytes("jpeg", quality=quality)


def compress_pdf_with_ghostscript(pdf_file: Union[str, bytes], 
                                 quality: str = "medium") -> bytes:
    """
    Alternative compression using Ghostscript (if available)
    """
    try:
        import subprocess
        import tempfile
        
        # Ghostscript settings
        gs_settings = {
            'low': ['/screen', '-dDownScaleFactor=2'],
            'medium': ['/ebook', '-dDownScaleFactor=2'],
            'high': ['/printer', '-dDownScaleFactor=4'],
            'maximum': ['/prepress', '-dDownScaleFactor=6']
        }
        
        settings = gs_settings.get(quality, gs_settings['medium'])
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_file:
            if isinstance(pdf_file, bytes):
                input_file.write(pdf_file)
            else:
                with open(pdf_file, 'rb') as f:
                    input_file.write(f.read())
            
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
            output_path = output_file.name
        
        # Run Ghostscript
        cmd = [
            'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/{}'.format(settings[0].replace('/', '')),
            '-dNOPAUSE', '-dQUIET', '-dBATCH',
            '-sOutputFile={}'.format(output_path),
            input_path
        ]
        
        if len(settings) > 1:
            cmd.extend(settings[1:])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Read compressed file
            with open(output_path, 'rb') as f:
                compressed_data = f.read()
            
            # Clean up temporary files
            os.unlink(input_path)
            os.unlink(output_path)
            
            return compressed_data
        else:
            raise Exception(f"Ghostscript error: {result.stderr}")
            
    except ImportError:
        raise PDFProcessingError("Ghostscript not available", "GHOSTSCRIPT_UNAVAILABLE")
    except Exception as e:
        raise PDFProcessingError(f"Ghostscript compression failed: {str(e)}", "GHOSTSCRIPT_ERROR")


def get_compression_preview(pdf_file: Union[str, bytes]) -> Dict[str, Any]:
    """
    Get compression preview for different quality levels
    """
    original_size = len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file)
    
    preview = {
        'original_size': original_size,
        'original_size_mb': original_size / 1024 / 1024,
        'quality_options': {}
    }
    
    quality_levels = ['low', 'medium', 'high', 'maximum']
    
    for quality in quality_levels:
        try:
            # Quick compression test (first page only)
            doc = fitz.open(pdf_file)
            if doc.page_count > 0:
                first_page = doc[0]
                temp_doc = fitz.open()
                new_page = temp_doc.new_page(width=first_page.rect.width, height=first_page.rect.height)
                new_page.show_pdf_page(first_page.rect, doc, 0)
                
                compressed_bytes = temp_doc.save(garbage=4, deflate=True)
                compressed_size = len(compressed_bytes)
                
                # Estimate full document size
                estimated_size = (compressed_size / 1) * doc.page_count
                compression_ratio = (1 - estimated_size / original_size) * 100
                
                preview['quality_options'][quality] = {
                    'estimated_size_mb': estimated_size / 1024 / 1024,
                    'compression_ratio': compression_ratio,
                    'description': get_quality_description(quality)
                }
                
                temp_doc.close()
            
            doc.close()
            
        except Exception as e:
            preview['quality_options'][quality] = {
                'error': str(e),
                'description': get_quality_description(quality)
            }
    
    return preview


def get_quality_description(quality: str) -> str:
    """Get description for quality level"""
    descriptions = {
        'low': 'Low compression - High quality, small size reduction',
        'medium': 'Medium compression - Balanced quality and size',
        'high': 'High compression - Lower quality, significant size reduction',
        'maximum': 'Maximum compression - Lowest quality, maximum size reduction'
    }
    return descriptions.get(quality, 'Unknown quality level')


def validate_compression_settings(quality: str, image_quality: int) -> Dict[str, Any]:
    """Validate compression settings"""
    errors = []
    
    valid_qualities = ['low', 'medium', 'high', 'maximum']
    if quality not in valid_qualities:
        errors.append(f"Quality must be one of: {', '.join(valid_qualities)}")
    
    if not isinstance(image_quality, int) or image_quality < 1 or image_quality > 100:
        errors.append("Image quality must be an integer between 1 and 100")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
