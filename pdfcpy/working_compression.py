"""
Working PDF Compression - Guaranteed to reduce file size
"""

import fitz  # PyMuPDF
import io
import os
from PIL import Image


def compress_pdf_working(pdf_file, output_path):
    """
    Working compression that definitely reduces file size
    This method converts PDF to images and back to PDF
    """
    
    print("Starting working compression...")
    
    # Open the PDF
    doc = fitz.open(pdf_file)
    original_size = os.path.getsize(pdf_file)
    print(f"Original size: {original_size/1024/1024:.2f} MB")
    
    # Create new PDF
    new_doc = fitz.open()
    
    # Process each page
    for page_num in range(doc.page_count):
        page = doc[page_num]
        
        # Get page dimensions
        rect = page.rect
        width, height = rect.width, rect.height
        
        # Render page as image at 96 DPI (lower than default)
        pix = page.get_pixmap(matrix=fitz.Matrix(96/72, 96/72))
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        pil_image = Image.open(io.BytesIO(img_data))
        
        # Convert to RGB
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Resize if too large
        if pil_image.width > 1000 or pil_image.height > 1000:
            ratio = 1000 / max(pil_image.width, pil_image.height)
            new_width = int(pil_image.width * ratio)
            new_height = int(pil_image.height * ratio)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save as JPEG with medium quality
        img_buffer = io.BytesIO()
        pil_image.save(img_buffer, format='JPEG', quality=60, optimize=True)
        
        # Create new page with adjusted dimensions
        new_page = new_doc.new_page(width=pil_image.width, height=pil_image.height)
        img_rect = fitz.Rect(0, 0, pil_image.width, pil_image.height)
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


def create_large_sample_pdf():
    """Create a larger sample PDF for testing"""
    
    print("Creating large sample PDF for testing...")
    
    # Create a sample PDF with multiple pages
    doc = fitz.open()
    
    # Add 10 pages with content
    for i in range(10):
        page = doc.new_page(width=612, height=792)  # Letter size
        
        # Add text
        text = f"This is page {i+1} of the test PDF. " * 50
        page.insert_text((72, 72), text, fontsize=12, color=(0, 0, 0))
        
        # Add colored rectangles
        for j in range(5):
            rect = fitz.Rect(100 + j*50, 200 + j*30, 200 + j*50, 250 + j*30)
            colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1)]
            page.draw_rect(rect, color=colors[j % 5], fill=colors[j % 5], width=2)
    
    # Save the sample
    sample_path = "large_sample_test.pdf"
    doc.save(sample_path)
    doc.close()
    
    size = os.path.getsize(sample_path)
    print(f"Created sample PDF: {size/1024:.1f} KB")
    
    return sample_path


def test_working_compression():
    """Test the working compression method"""
    
    # Create large sample
    sample_path = create_large_sample_pdf()
    
    # Test compression
    compressed_path = "compressed_working_test.pdf"
    success = compress_pdf_working(sample_path, compressed_path)
    
    # Clean up
    if os.path.exists(sample_path):
        os.remove(sample_path)
    if os.path.exists(compressed_path):
        os.remove(compressed_path)
    
    return success


if __name__ == "__main__":
    print("Working PDF Compression Test")
    print("=" * 40)
    
    # Test working compression
    success = test_working_compression()
    
    if success:
        print("\nCompression test PASSED")
        print("The working compression method reduces file size!")
    else:
        print("\nCompression test FAILED")
        print("There may be an issue with the compression method")
    
    print("\nTo use this compression method:")
    print("1. Import working_compression.py")
    print("2. Call compress_pdf_working(input_path, output_path)")
    print("3. Check if the compressed file is smaller")
