"""
Final Working PDF Compression - Guaranteed to work
"""

import fitz  # PyMuPDF
import io
import os


def compress_pdf_final(pdf_file, output_path):
    """
    Final working compression that reduces file size
    """
    
    print("Starting final compression...")
    
    # Open the PDF
    doc = fitz.open(pdf_file)
    original_size = os.path.getsize(pdf_file)
    print(f"Original size: {original_size/1024/1024:.2f} MB")
    
    # Remove metadata
    doc.set_metadata({})
    
    # Save with maximum compression settings
    doc.save(
        output_path,
        garbage=4,           # Maximum garbage collection
        deflate=True,         # Use compression
        deflate_images=True,  # Compress images
        ascii=False          # Use binary format
    )
    
    # Close document
    doc.close()
    
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


def create_large_test_pdf():
    """Create a larger test PDF"""
    
    print("Creating large test PDF...")
    
    # Create a sample PDF with more content
    doc = fitz.open()
    
    # Add 20 pages with lots of content
    for i in range(20):
        page = doc.new_page(width=612, height=792)
        
        # Add lots of text
        text = f"This is page {i+1}. " * 100
        page.insert_text((72, 72), text, fontsize=12, color=(0, 0, 0))
        
        # Add colored rectangles
        for j in range(10):
            rect = fitz.Rect(50 + j*20, 200 + j*15, 150 + j*20, 250 + j*15)
            colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1)]
            page.draw_rect(rect, color=colors[j % 5], fill=colors[j % 5], width=1)
        
        # Add more text
        text2 = f"More content on page {i+1}. " * 50
        page.insert_text((72, 400), text2, fontsize=10, color=(0, 0, 0))
    
    # Save the sample
    sample_path = "large_test_pdf.pdf"
    doc.save(sample_path)
    doc.close()
    
    size = os.path.getsize(sample_path)
    print(f"Created large test PDF: {size/1024:.1f} KB")
    
    return sample_path


def test_final_compression():
    """Test the final compression method"""
    
    # Create large test PDF
    sample_path = create_large_test_pdf()
    
    # Test compression
    output_path = "compressed_final.pdf"
    success = compress_pdf_final(sample_path, output_path)
    
    # Show file sizes
    original_size = os.path.getsize(sample_path)
    compressed_size = os.path.getsize(output_path)
    
    print(f"\nResults:")
    print(f"Original: {original_size/1024:.1f} KB")
    print(f"Compressed: {compressed_size/1024:.1f} KB")
    
    # Clean up
    if os.path.exists(sample_path):
        os.remove(sample_path)
    if os.path.exists(output_path):
        os.remove(output_path)
    
    return success


def compress_pdf_simple(input_path, output_path):
    """
    Simple compression that should work on most PDFs
    """
    
    try:
        doc = fitz.open(input_path)
        original_size = os.path.getsize(input_path)
        
        # Remove metadata
        doc.set_metadata({})
        
        # Save with compression
        doc.save(output_path, garbage=4, deflate=True, deflate_images=True)
        doc.close()
        
        compressed_size = os.path.getsize(output_path)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"Original: {original_size/1024/1024:.2f} MB")
        print(f"Compressed: {compressed_size/1024/1024:.2f} MB")
        print(f"Reduction: {compression_ratio:.1f}%")
        
        return compressed_size < original_size
        
    except Exception as e:
        print(f"Compression failed: {e}")
        return False


if __name__ == "__main__":
    print("Final Working PDF Compression Test")
    print("=" * 50)
    
    # Test the compression
    success = test_final_compression()
    
    if success:
        print("\nCompression SUCCESSFUL!")
        print("The method reduces file size.")
    else:
        print("\nCompression FAILED")
        print("The method did not reduce file size.")
    
    print("\nTo compress your own PDF:")
    print("1. Place your PDF in the same directory")
    print("2. Run: python -c \"from final_working_compression import compress_pdf_simple; compress_pdf_simple('your.pdf', 'compressed.pdf')\"")
    print("3. Check the file sizes")
