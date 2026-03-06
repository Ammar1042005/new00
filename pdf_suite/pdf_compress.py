"""
PDF Compress Tool - Reduce PDF file size while maintaining quality
"""

import io
import os
from typing import Union, Dict, Any
from PyMuPDF import fitz

def compress_pdf(pdf_file: Union[str, bytes],
                quality: str = "medium",
                image_quality: int = 75,
                output_path: str = None) -> bytes:
    """
    Compress PDF by reducing image quality and removing unnecessary data
    
    Args:
        pdf_file: PDF file path or bytes
        quality: Compression level (low, medium, high, maximum)
        image_quality: Image quality (1-100)
        output_path: Optional output file path
    
    Returns:
        bytes: Compressed PDF data
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            if not os.path.exists(pdf_file):
                raise FileNotFoundError(f"PDF file not found: {pdf_file}")
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Get compression settings
        compression_settings = _get_compression_settings(quality)
        
        # Create new PDF with compression
        compressed_pdf = fitz.open()
        
        # Process each page
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            
            # Extract page as image with compression
            pix = page.get_pixmap(
                dpi=compression_settings['dpi'],
                alpha=False
            )
            
            # Convert to compressed image
            img_data = pix.tobytes("jpeg", quality=image_quality)
            
            # Create new page from image
            img_rect = fitz.Rect(0, 0, pix.width, pix.height)
            new_page = compressed_pdf.new_page(
                width=pix.width,
                height=pix.height
            )
            
            # Insert compressed image
            new_page.insert_image(img_rect, img_data)
        
        # Copy metadata from original
        metadata = pdf_doc.metadata
        compressed_pdf.set_metadata(metadata)
        
        # Save compressed PDF
        compressed_bytes = compressed_pdf.write()
        
        pdf_doc.close()
        compressed_pdf.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(compressed_bytes)
        
        return compressed_bytes
        
    except Exception as e:
        raise ValueError(f"Error compressing PDF: {str(e)}")

def compress_pdf_advanced(pdf_file: Union[str, bytes],
                      settings: Dict[str, Any],
                      output_path: str = None) -> bytes:
    """
    Advanced PDF compression with custom settings
    
    Args:
        pdf_file: PDF file path or bytes
        settings: Compression settings dictionary
        output_path: Optional output file path
    
    Returns:
        bytes: Compressed PDF data
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Default settings
        default_settings = {
            'dpi': 150,
            'image_quality': 75,
            'remove_annotations': True,
            'remove_form_fields': True,
            'optimize_fonts': True,
            'compress_text': True
        }
        
        # Merge with custom settings
        settings = {**default_settings, **settings}
        
        # Create new PDF
        compressed_pdf = fitz.open()
        
        # Process each page with advanced settings
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            
            # Create new page with same dimensions
            rect = page.rect
            new_page = compressed_pdf.new_page(
                width=rect.width,
                height=rect.height
            )
            
            # Copy page content with optimization
            if settings['compress_text']:
                # Extract text and reinsert with compression
                text_dict = page.get_text("dict")
                for block in text_dict.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                new_page.insert_text(
                                    span["bbox"][:2],
                                    span["text"],
                                    fontname=span.get("font", "helv"),
                                    fontsize=span.get("size", 12),
                                    color=span.get("color", 0)
                                )
            
            # Extract and compress images
            image_list = page.get_images()
            for img in image_list:
                try:
                    # Get image data
                    xref = img[0]
                    base_image = pdf_doc.extract_image(xref)
                    
                    # Compress image
                    img_data = base_image["image"]
                    img_rect = fitz.Rect(img[2], img[3], img[2] + base_image["width"], img[3] + base_image["height"])
                    
                    # Insert compressed image
                    new_page.insert_image(img_rect, img_data)
                except:
                    continue  # Skip problematic images
        
        # Copy and optimize metadata
        metadata = pdf_doc.metadata
        if settings['optimize_fonts']:
            # Remove font information to reduce size
            metadata.pop('creator', None)
            metadata.pop('producer', None)
            metadata.pop('format', None)
        
        compressed_pdf.set_metadata(metadata)
        
        # Save compressed PDF
        compressed_bytes = compressed_pdf.write()
        
        pdf_doc.close()
        compressed_pdf.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(compressed_bytes)
        
        return compressed_bytes
        
    except Exception as e:
        raise ValueError(f"Error in advanced PDF compression: {str(e)}")

def compress_pdf_ghostscript(pdf_file: Union[str, bytes],
                          quality: str = "medium",
                          output_path: str = None) -> bytes:
    """
    Compress PDF using Ghostscript (if available)
    
    Args:
        pdf_file: PDF file path or bytes
        quality: Compression level
        output_path: Optional output file path
    
    Returns:
        bytes: Ghostscript compressed PDF data
    """
    try:
        import subprocess
        import tempfile
        
        # Ghostscript settings
        gs_settings = {
            "screen": "-dPDFSETTINGS=/screen",
            "ebook": "-dPDFSETTINGS=/ebook",
            "printer": "-dPDFSETTINGS=/printer",
            "prepress": "-dPDFSETTINGS=/prepress"
        }
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as input_file:
            if isinstance(pdf_file, str):
                with open(pdf_file, 'rb') as f:
                    input_file.write(f.read())
            else:
                input_file.write(pdf_file)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output_file:
            output_path_gs = output_file.name
        
        # Run Ghostscript
        gs_command = [
            "gswin64c",  # or "gs" on Linux/Mac
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            gs_settings.get(quality, "-dPDFSETTINGS=/ebook"),
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path_gs}",
            input_path
        ]
        
        try:
            subprocess.run(gs_command, check=True, capture_output=True)
            
            # Read compressed result
            with open(output_path_gs, 'rb') as f:
                compressed_bytes = f.read()
            
            return compressed_bytes
            
        except subprocess.CalledProcessError as e:
            print(f"Ghostscript compression failed: {e}")
            # Fall back to regular compression
            return compress_pdf(pdf_file, quality)
        
        finally:
            # Clean up temporary files
            try:
                os.unlink(input_path)
                os.unlink(output_path_gs)
            except:
                pass
        
    except ImportError:
        # Ghostscript not available, use regular compression
        return compress_pdf(pdf_file, quality)
    except Exception as e:
        raise ValueError(f"Error in Ghostscript compression: {str(e)}")

def get_compression_info(pdf_file: Union[str, bytes]) -> Dict[str, Any]:
    """
    Get compression information about PDF
    
    Args:
        pdf_file: PDF file path or bytes
    
    Returns:
        dict: Compression information
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Get file size
        if isinstance(pdf_file, str):
            original_size = os.path.getsize(pdf_file)
        else:
            original_size = len(pdf_file)
        
        # Analyze content
        total_images = 0
        total_text_chars = 0
        
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            
            # Count images
            images = page.get_images()
            total_images += len(images)
            
            # Count text characters
            text = page.get_text()
            total_text_chars += len(text)
        
        pdf_doc.close()
        
        return {
            'original_size': original_size,
            'original_size_mb': round(original_size / (1024 * 1024), 2),
            'total_pages': len(pdf_doc),
            'total_images': total_images,
            'total_text_chars': total_text_chars,
            'estimated_compression_ratio': _estimate_compression_ratio(total_images, total_text_chars)
        }
        
    except Exception as e:
        raise ValueError(f"Error getting compression info: {str(e)}")

def _get_compression_settings(quality: str) -> Dict[str, int]:
    """Get compression settings based on quality level"""
    settings = {
        "low": {'dpi': 100, 'image_quality': 50},
        "medium": {'dpi': 150, 'image_quality': 75},
        "high": {'dpi': 200, 'image_quality': 85},
        "maximum": {'dpi': 300, 'image_quality': 95}
    }
    return settings.get(quality, settings["medium"])

def _estimate_compression_ratio(images: int, text_chars: int) -> float:
    """Estimate potential compression ratio"""
    # Heuristic based on content analysis
    if images > text_chars / 1000:  # Image-heavy
        return 0.3  # Can compress to 30% of original
    elif text_chars > images * 5000:  # Text-heavy
        return 0.7  # Can compress to 70% of original
    else:  # Mixed content
        return 0.5  # Can compress to 50% of original

# Example usage and testing
if __name__ == "__main__":
    # Test compression functionality
    test_file = "test.pdf"  # Replace with actual test file
    
    try:
        # Get compression info
        info = get_compression_info(test_file)
        print(f"Original file info: {info}")
        
        # Test basic compression
        compressed = compress_pdf(test_file, "medium", 75, "compressed_medium.pdf")
        print("PDF compressed with medium quality!")
        
        # Test advanced compression
        settings = {
            'dpi': 120,
            'image_quality': 60,
            'remove_annotations': True,
            'optimize_fonts': True
        }
        advanced_compressed = compress_pdf_advanced(test_file, settings, "compressed_advanced.pdf")
        print("PDF compressed with advanced settings!")
        
        # Test Ghostscript compression
        gs_compressed = compress_pdf_ghostscript(test_file, "ebook", "compressed_gs.pdf")
        print("PDF compressed with Ghostscript!")
        
    except Exception as e:
        print(f"Error during compression: {str(e)}")
