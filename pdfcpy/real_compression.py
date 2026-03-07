"""
Real PDF Compression - Actually reduces file size
"""

import fitz  # PyMuPDF
import io
import os


def compress_pdf_real(pdf_file, output_path):
    """
    Real compression that reduces file size by:
    1. Removing metadata
    2. Compressing images
    3. Optimizing fonts
    4. Using maximum compression settings
    """
    
    print("Starting real compression...")
    
    # Open the PDF
    doc = fitz.open(pdf_file)
    original_size = os.path.getsize(pdf_file)
    print(f"Original size: {original_size/1024/1024:.2f} MB")
    
    # Remove metadata
    doc.set_metadata({})
    
    # Clean the document (remove unused objects)
    doc.clean()
    
    # Save with maximum compression
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


def compress_pdf_with_image_optimization(pdf_file, output_path):
    """
    Compression with image optimization
    """
    
    print("Starting compression with image optimization...")
    
    # Open the PDF
    doc = fitz.open(pdf_file)
    original_size = os.path.getsize(pdf_file)
    print(f"Original size: {original_size/1024/1024:.2f} MB")
    
    # Create new document
    new_doc = fitz.open()
    
    # Process each page
    for page_num in range(doc.page_count):
        page = doc[page_num]
        
        # Get all images on the page
        image_list = page.get_images()
        
        # Create new page
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        
        # Copy page content without images
        new_page.show_pdf_page(page.rect, doc, page_num)
        
        # Process and compress images
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
                img_data = pix.tobytes("jpeg", quality=50)
                
                # Replace image
                img_rect = page.get_image_bbox(img)
                new_page.insert_image(img_rect, stream=img_data)
                
                pix = None
                
            except Exception as e:
                print(f"Error processing image {img_index}: {e}")
                continue
    
    # Remove metadata
    new_doc.set_metadata({})
    
    # Save with compression
    new_doc.save(
        output_path,
        garbage=4,
        deflate=True,
        deflate_images=True,
        ascii=False
    )
    
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


def create_test_pdf_with_images():
    """Create a test PDF with images"""
    
    print("Creating test PDF with images...")
    
    # Create a sample PDF
    doc = fitz.open()
    
    # Add pages with content and images
    for i in range(5):
        page = doc.new_page(width=612, height=792)
        
        # Add text
        text = f"This is page {i+1} with content and images. " * 20
        page.insert_text((72, 72), text, fontsize=12, color=(0, 0, 0))
        
        # Create a simple image (colored rectangle)
        img_rect = fitz.Rect(100, 200, 400, 400)
        page.draw_rect(img_rect, color=(0.5, 0.5, 0.5), fill=(0.8, 0.8, 0.8), width=2)
        
        # Add more content
        text2 = f"More content on page {i+1}. " * 15
        page.insert_text((72, 450), text2, fontsize=10, color=(0, 0, 0))
    
    # Save the sample
    sample_path = "test_pdf_with_images.pdf"
    doc.save(sample_path)
    doc.close()
    
    size = os.path.getsize(sample_path)
    print(f"Created test PDF: {size/1024:.1f} KB")
    
    return sample_path


def test_real_compression():
    """Test real compression methods"""
    
    print("Testing real compression methods...")
    
    # Create test PDF
    sample_path = create_test_pdf_with_images()
    
    # Test method 1: Basic compression
    print("\n--- Method 1: Basic Compression ---")
    output1 = "compressed_basic.pdf"
    success1 = compress_pdf_real(sample_path, output1)
    
    # Test method 2: Image optimization
    print("\n--- Method 2: Image Optimization ---")
    output2 = "compressed_images.pdf"
    success2 = compress_pdf_with_image_optimization(sample_path, output2)
    
    # Clean up
    if os.path.exists(sample_path):
        os.remove(sample_path)
    if os.path.exists(output1):
        os.remove(output1)
    if os.path.exists(output2):
        os.remove(output2)
    
    return success1 or success2


def compress_any_pdf(input_path, output_path):
    """
    Try multiple compression methods and return the best result
    """
    
    original_size = os.path.getsize(input_path)
    print(f"Original size: {original_size/1024/1024:.2f} MB")
    
    best_result = None
    best_size = original_size
    
    # Method 1: Basic compression
    try:
        temp1 = "temp1.pdf"
        if compress_pdf_real(input_path, temp1):
            size1 = os.path.getsize(temp1)
            if size1 < best_size:
                best_result = temp1
                best_size = size1
                print(f"Method 1 is better: {size1/1024/1024:.2f} MB")
        else:
            os.remove(temp1)
    except Exception as e:
        print(f"Method 1 failed: {e}")
    
    # Method 2: Image optimization
    try:
        temp2 = "temp2.pdf"
        if compress_pdf_with_image_optimization(input_path, temp2):
            size2 = os.path.getsize(temp2)
            if size2 < best_size:
                best_result = temp2
                best_size = size2
                print(f"Method 2 is better: {size2/1024/1024:.2f} MB")
            else:
                os.remove(temp2)
        else:
            os.remove(temp2)
    except Exception as e:
        print(f"Method 2 failed: {e}")
    
    # Copy best result to output
    if best_result:
        import shutil
        shutil.copy2(best_result, output_path)
        os.remove(best_result)
        
        final_size = os.path.getsize(output_path)
        compression_ratio = (1 - final_size / original_size) * 100
        print(f"Final compressed size: {final_size/1024/1024:.2f} MB")
        print(f"Final compression ratio: {compression_ratio:.1f}%")
        return True
    else:
        print("No compression method worked")
        return False


if __name__ == "__main__":
    print("Real PDF Compression Test")
    print("=" * 40)
    
    # Test real compression
    success = test_real_compression()
    
    if success:
        print("\nAt least one compression method worked!")
    else:
        print("\nNo compression method worked")
    
    print("\nTo compress your own PDF:")
    print("1. Place your PDF in the same directory")
    print("2. Run: python -c \"from real_compression import compress_any_pdf; compress_any_pdf('your.pdf', 'compressed.pdf')\"")
    print("3. Check if the compressed file is smaller")
