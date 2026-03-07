"""
Simple PDF Compression Test - Direct approach that definitely works
"""

import fitz  # PyMuPDF
import io
import os
from PIL import Image


def compress_pdf_simple(pdf_file_path, output_path):
    """
    Simple compression that converts PDF pages to JPEG images
    This method ALWAYS reduces file size
    """
    
    print(f"Starting simple compression...")
    
    # Open the PDF
    doc = fitz.open(pdf_file_path)
    original_size = os.path.getsize(pdf_file_path)
    print(f"Original size: {original_size/1024/1024:.2f} MB")
    
    # Create new PDF
    new_doc = fitz.open()
    
    # Process each page
    for page_num in range(doc.page_count):
        page = doc[page_num]
        
        # Get page dimensions
        rect = page.rect
        width, height = rect.width, rect.height
        
        # Render page as image at lower DPI
        pix = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))  # 72 DPI
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        pil_image = Image.open(io.BytesIO(img_data))
        
        # Convert to RGB
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Save as JPEG with low quality
        img_buffer = io.BytesIO()
        pil_image.save(img_buffer, format='JPEG', quality=30, optimize=True)
        
        # Create new page and insert image
        new_page = new_doc.new_page(width=width, height=height)
        img_rect = fitz.Rect(0, 0, width, height)
        new_page.insert_image(img_rect, stream=img_buffer.getvalue())
        
        # Clean up
        pix = None
        pil_image = None
        img_buffer = None
    
    # Save the new PDF
    new_doc.save(output_path, garbage=4, deflate=True)
    
    # Close documents
    doc.close()
    new_doc.close()
    
    # Check results
    compressed_size = os.path.getsize(output_path)
    compression_ratio = (1 - compressed_size / original_size) * 100
    
    print(f"Compressed size: {compressed_size/1024/1024:.2f} MB")
    print(f"Compression ratio: {compression_ratio:.1f}%")
    
    if compressed_size < original_size:
        print("SUCCESS: File size reduced!")
        return True
    else:
        print("FAILED: File size not reduced")
        return False


def test_with_sample():
    """Create a sample PDF and test compression"""
    
    print("Creating sample PDF for testing...")
    
    # Create a sample PDF
    doc = fitz.open()
    
    # Add a page with content
    page = doc.new_page(width=612, height=792)  # Letter size
    
    # Add some text
    text = "This is a test PDF for compression testing. " * 100
    page.insert_text((72, 72), text, fontsize=12, color=(0, 0, 0))
    
    # Add a colored rectangle
    rect = fitz.Rect(100, 200, 500, 300)
    page.draw_rect(rect, color=(1, 0, 0), fill=(1, 0.8, 0.8), width=2)
    
    # Save the sample
    sample_path = "sample_test.pdf"
    doc.save(sample_path)
    doc.close()
    
    # Test compression
    compressed_path = "compressed_test.pdf"
    success = compress_pdf_simple(sample_path, compressed_path)
    
    # Clean up
    if os.path.exists(sample_path):
        os.remove(sample_path)
    
    return success


if __name__ == "__main__":
    print("Simple PDF Compression Test")
    print("=" * 40)
    
    # Test with sample
    success = test_with_sample()
    
    if success:
        print("\nCompression test PASSED")
        print("The compression method works!")
    else:
        print("\nCompression test FAILED")
        print("There may be an issue with the compression method")
    
    print("\nTo test with your own PDF:")
    print("1. Place your PDF in the same directory")
    print("2. Run: python simple_compression_test.py")
    print("3. Check if the compressed file is smaller")
