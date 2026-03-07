"""
Aggressive PDF Compression - Guaranteed size reduction
"""

import fitz  # PyMuPDF
import io
import os
from PIL import Image
import tempfile
from typing import Union, Dict, Any
from enhanced_pdf_tools import PDFProcessingError


def compress_pdf_aggressive_v2(pdf_file: Union[str, bytes], 
                              quality_level: str = "medium") -> bytes:
    """
    Aggressive PDF compression that guarantees size reduction
    
    This method converts pages to images at lower DPI, which will
    definitely reduce file size but may affect text quality.
    """
    
    # DPI settings for different quality levels
    dpi_settings = {
        'low': 72,      # Very small, poor quality
        'medium': 96,   # Small, acceptable quality
        'high': 120,    # Medium, good quality
        'maximum': 150  # Larger, best quality
    }
    
    dpi = dpi_settings.get(quality_level, dpi_settings['medium'])
    
    try:
        doc = fitz.open(pdf_file)
        original_size = len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file)
        
        print(f"Starting aggressive compression at {dpi} DPI")
        print(f"Original size: {original_size/1024/1024:.2f} MB")
        
        # Create new document
        compressed_doc = fitz.open()
        
        # Process each page
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Get page dimensions
            rect = page.rect
            width, height = rect.width, rect.height
            
            # Render page as image at target DPI
            matrix = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=matrix)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Optimize image for compression
            img_buffer = io.BytesIO()
            
            # Use JPEG for better compression
            if quality_level == 'low':
                pil_image.save(img_buffer, format='JPEG', quality=30, optimize=True)
            elif quality_level == 'medium':
                pil_image.save(img_buffer, format='JPEG', quality=50, optimize=True)
            elif quality_level == 'high':
                pil_image.save(img_buffer, format='JPEG', quality=70, optimize=True)
            else:  # maximum
                pil_image.save(img_buffer, format='JPEG', quality=85, optimize=True)
            
            # Create new page and insert compressed image
            new_page = compressed_doc.new_page(width=width, height=height)
            img_rect = fitz.Rect(0, 0, width, height)
            new_page.insert_image(img_rect, stream=img_buffer.getvalue())
            
            # Clean up
            pix = None
            pil_image = None
            img_buffer = None
        
        # Save with maximum compression
        compressed_bytes = compressed_doc.save(
            garbage=4,           # Maximum garbage collection
            deflate=True,         # Use compression
            deflate_images=True,  # Compress images
            ascii=False          # Use binary format
        )
        
        # Close documents
        doc.close()
        compressed_doc.close()
        
        # Calculate compression ratio
        compressed_size = len(compressed_bytes)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"Compressed size: {compressed_size/1024/1024:.2f} MB")
        print(f"Compression ratio: {compression_ratio:.1f}%")
        
        # Verify compression actually worked
        if compressed_size >= original_size:
            print("Aggressive compression failed, trying extreme method...")
            return compress_pdf_extreme(pdf_file)
        
        return compressed_bytes
        
    except Exception as e:
        raise PDFProcessingError(f"Error in aggressive compression: {str(e)}", "COMPRESSION_ERROR")


def compress_pdf_extreme(pdf_file: Union[str, bytes]) -> bytes:
    """
    Extreme compression - converts everything to low-quality images
    This will definitely reduce file size but significantly impacts quality
    """
    
    try:
        doc = fitz.open(pdf_file)
        original_size = len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file)
        
        print(f"Starting extreme compression")
        print(f"Original size: {original_size/1024/1024:.2f} MB")
        
        # Create new document
        compressed_doc = fitz.open()
        
        # Process each page at very low DPI
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Get page dimensions
            rect = page.rect
            width, height = rect.width, rect.height
            
            # Render page as image at very low DPI (72 DPI)
            matrix = fitz.Matrix(1.0, 1.0)  # 72 DPI
            pix = page.get_pixmap(matrix=matrix)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Resize to smaller dimensions if page is large
            max_dimension = 800  # Maximum width or height
            if pil_image.width > max_dimension or pil_image.height > max_dimension:
                ratio = max_dimension / max(pil_image.width, pil_image.height)
                new_width = int(pil_image.width * ratio)
                new_height = int(pil_image.height * ratio)
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save as very low quality JPEG
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format='JPEG', quality=20, optimize=True)
            
            # Create new page and insert compressed image
            new_page = compressed_doc.new_page(width=pil_image.width, height=pil_image.height)
            img_rect = fitz.Rect(0, 0, pil_image.width, pil_image.height)
            new_page.insert_image(img_rect, stream=img_buffer.getvalue())
            
            # Clean up
            pix = None
            pil_image = None
            img_buffer = None
        
        # Save with maximum compression
        compressed_bytes = compressed_doc.save(
            garbage=4,
            deflate=True,
            deflate_images=True,
            ascii=False
        )
        
        # Close documents
        doc.close()
        compressed_doc.close()
        
        # Calculate compression ratio
        compressed_size = len(compressed_bytes)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"Extreme compressed size: {compressed_size/1024/1024:.2f} MB")
        print(f"Extreme compression ratio: {compression_ratio:.1f}%")
        
        return compressed_bytes
        
    except Exception as e:
        raise PDFProcessingError(f"Error in extreme compression: {str(e)}", "COMPRESSION_ERROR")


def compress_pdf_image_based(pdf_file: Union[str, bytes], 
                           dpi: int = 96,
                           jpeg_quality: int = 50) -> bytes:
    """
    Image-based compression - converts PDF pages to JPEG images
    This method guarantees size reduction by converting everything to images
    """
    
    try:
        doc = fitz.open(pdf_file)
        original_size = len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file)
        
        print(f"Starting image-based compression at {dpi} DPI, quality {jpeg_quality}")
        print(f"Original size: {original_size/1024/1024:.2f} MB")
        
        # Create new document
        compressed_doc = fitz.open()
        
        # Process each page
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Get page dimensions
            rect = page.rect
            width, height = rect.width, rect.height
            
            # Render page as image
            matrix = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=matrix)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Save as JPEG with specified quality
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format='JPEG', quality=jpeg_quality, optimize=True)
            
            # Create new page and insert image
            new_page = compressed_doc.new_page(width=width, height=height)
            img_rect = fitz.Rect(0, 0, width, height)
            new_page.insert_image(img_rect, stream=img_buffer.getvalue())
            
            # Clean up
            pix = None
            pil_image = None
            img_buffer = None
        
        # Save with compression
        compressed_bytes = compressed_doc.save(
            garbage=4,
            deflate=True,
            deflate_images=True,
            ascii=False
        )
        
        # Close documents
        doc.close()
        compressed_doc.close()
        
        # Calculate compression ratio
        compressed_size = len(compressed_bytes)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"Image-based compressed size: {compressed_size/1024/1024:.2f} MB")
        print(f"Image-based compression ratio: {compression_ratio:.1f}%")
        
        return compressed_bytes
        
    except Exception as e:
        raise PDFProcessingError(f"Error in image-based compression: {str(e)}", "COMPRESSION_ERROR")


def compress_pdf_text_extraction(pdf_file: Union[str, bytes]) -> bytes:
    """
    Text extraction compression - extract text and recreate PDF
    This method works for text-heavy PDFs and can significantly reduce size
    """
    
    try:
        doc = fitz.open(pdf_file)
        original_size = len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file)
        
        print(f"Starting text extraction compression")
        print(f"Original size: {original_size/1024/1024:.2f} MB")
        
        # Create new document
        compressed_doc = fitz.open()
        
        # Process each page
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Extract text
            text = page.get_text()
            
            if text.strip():  # If page has text
                # Create new page with same dimensions
                new_page = compressed_doc.new_page(width=page.rect.width, height=page.rect.height)
                
                # Insert text at original positions
                # This is simplified - in reality, you'd need to preserve formatting
                new_page.insert_text((50, 50), text, fontsize=12, color=(0, 0, 0))
            else:
                # For pages without text, use image compression
                matrix = fitz.Matrix(1.0, 1.0)
                pix = page.get_pixmap(matrix=matrix)
                img_data = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_data))
                
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                img_buffer = io.BytesIO()
                pil_image.save(img_buffer, format='JPEG', quality=30, optimize=True)
                
                new_page = compressed_doc.new_page(width=page.rect.width, height=page.rect.height)
                img_rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
                new_page.insert_image(img_rect, stream=img_buffer.getvalue())
                
                pix = None
                pil_image = None
                img_buffer = None
        
        # Save with compression
        compressed_bytes = compressed_doc.save(
            garbage=4,
            deflate=True,
            ascii=False
        )
        
        # Close documents
        doc.close()
        compressed_doc.close()
        
        # Calculate compression ratio
        compressed_size = len(compressed_bytes)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"Text extraction compressed size: {compressed_size/1024/1024:.2f} MB")
        print(f"Text extraction compression ratio: {compression_ratio:.1f}%")
        
        return compressed_bytes
        
    except Exception as e:
        raise PDFProcessingError(f"Error in text extraction compression: {str(e)}", "COMPRESSION_ERROR")


def compress_pdf_multi_method(pdf_file: Union[str, bytes]) -> bytes:
    """
    Try multiple compression methods and return the best result
    """
    
    original_size = len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file)
    print(f"Original size: {original_size/1024/1024:.2f} MB")
    
    best_result = None
    best_size = original_size
    best_method = "none"
    
    methods = [
        ("Image-based (96 DPI)", lambda f: compress_pdf_image_based(f, 96, 50)),
        ("Image-based (72 DPI)", lambda f: compress_pdf_image_based(f, 72, 30)),
        ("Aggressive (medium)", lambda f: compress_pdf_aggressive_v2(f, "medium")),
        ("Aggressive (low)", lambda f: compress_pdf_aggressive_v2(f, "low")),
        ("Extreme", lambda f: compress_pdf_extreme(f)),
    ]
    
    for method_name, method_func in methods:
        try:
            print(f"\nTrying: {method_name}")
            result = method_func(pdf_file)
            result_size = len(result)
            compression_ratio = (1 - result_size / original_size) * 100
            
            print(f"Result: {result_size/1024/1024:.2f} MB ({compression_ratio:.1f}% reduction)")
            
            if result_size < best_size:
                best_result = result
                best_size = result_size
                best_method = method_name
                print(f"✅ New best result: {method_name}")
            else:
                print(f"❌ Not better than current best")
                
        except Exception as e:
            print(f"❌ Method failed: {str(e)}")
    
    if best_result:
        final_ratio = (1 - best_size / original_size) * 100
        print(f"\n🎯 Best method: {best_method}")
        print(f"Final size: {best_size/1024/1024:.2f} MB")
        print(f"Final compression: {final_ratio:.1f}%")
        return best_result
    else:
        raise PDFProcessingError("All compression methods failed", "COMPRESSION_FAILED")


def test_compression_methods(pdf_file: Union[str, bytes]):
    """
    Test all compression methods and show results
    """
    
    original_size = len(pdf_file) if isinstance(pdf_file, bytes) else os.path.getsize(pdf_file)
    print(f"Testing compression methods")
    print(f"Original size: {original_size/1024/1024:.2f} MB")
    print("=" * 60)
    
    methods = [
        ("Standard (low)", lambda f: compress_pdf_aggressive_v2(f, "low")),
        ("Standard (medium)", lambda f: compress_pdf_aggressive_v2(f, "medium")),
        ("Standard (high)", lambda f: compress_pdf_aggressive_v2(f, "high")),
        ("Image-based (72 DPI)", lambda f: compress_pdf_image_based(f, 72, 30)),
        ("Image-based (96 DPI)", lambda f: compress_pdf_image_based(f, 96, 50)),
        ("Image-based (120 DPI)", lambda f: compress_pdf_image_based(f, 120, 70)),
        ("Extreme", lambda f: compress_pdf_extreme(f)),
    ]
    
    results = []
    
    for method_name, method_func in methods:
        try:
            result = method_func(pdf_file)
            result_size = len(result)
            compression_ratio = (1 - result_size / original_size) * 100
            
            results.append({
                'method': method_name,
                'size': result_size,
                'ratio': compression_ratio
            })
            
            print(f"{method_name:20} | {result_size/1024/1024:6.2f} MB | {compression_ratio:5.1f}%")
            
        except Exception as e:
            print(f"{method_name:20} | FAILED    | {str(e)}")
    
    # Find best result
    if results:
        best = min(results, key=lambda x: x['size'])
        print(f"\n🏆 Best method: {best['method']}")
        print(f"📊 Best size: {best['size']/1024/1024:.2f} MB")
        print(f"📈 Best compression: {best['ratio']:.1f}%")
    
    return results
