"""
Test script for enhanced PDF compression functionality
"""

import os
import sys
from enhanced_compression import (
    compress_pdf_enhanced,
    compress_pdf_with_ghostscript,
    get_compression_preview,
    validate_compression_settings
)

def test_compression_functionality():
    """Test the enhanced compression functionality"""
    print("🧪 Testing Enhanced PDF Compression")
    print("=" * 50)
    
    # Test validation
    print("\n1. Testing Compression Settings Validation")
    validation = validate_compression_settings('medium', 75)
    if validation['valid']:
        print("✅ Valid settings passed validation")
    else:
        print(f"❌ Valid settings failed: {validation['errors']}")
    
    # Test invalid settings
    validation = validate_compression_settings('invalid', 150)
    if not validation['valid']:
        print("✅ Invalid settings correctly rejected")
    else:
        print("❌ Invalid settings were accepted")
    
    # Test with sample PDF if available
    test_file = "test_files/sample.pdf"
    if os.path.exists(test_file):
        print(f"\n2. Testing Compression with {test_file}")
        
        try:
            # Get original size
            original_size = os.path.getsize(test_file)
            print(f"Original size: {original_size/1024/1024:.2f} MB")
            
            # Test compression preview
            print("\n2.1. Testing Compression Preview")
            preview = get_compression_preview(test_file)
            print(f"Preview generated for {len(preview['quality_options'])} quality levels")
            
            for quality, option in preview['quality_options'].items():
                if 'error' not in option:
                    print(f"  {quality}: {option['estimated_size_mb']:.2f} MB ({option['compression_ratio']:.1f}% reduction)")
                else:
                    print(f"  {quality}: Error - {option['error']}")
            
            # Test actual compression
            print("\n2.2. Testing Actual Compression")
            qualities = ['low', 'medium', 'high']
            
            for quality in qualities:
                try:
                    compressed_data = compress_pdf_enhanced(test_file, quality=quality)
                    compressed_size = len(compressed_data)
                    compression_ratio = (1 - compressed_size / original_size) * 100
                    
                    print(f"  {quality}: {compressed_size/1024/1024:.2f} MB ({compression_ratio:.1f}% reduction)")
                    
                    # Verify compression actually reduced size
                    if compressed_size < original_size:
                        print(f"    ✅ Compression successful")
                    else:
                        print(f"    ⚠️  No size reduction achieved")
                    
                except Exception as e:
                    print(f"  {quality}: Error - {str(e)}")
            
            # Test Ghostscript compression (if available)
            print("\n2.3. Testing Ghostscript Compression")
            try:
                gs_compressed = compress_pdf_with_ghostscript(test_file, quality='medium')
                gs_size = len(gs_compressed)
                gs_ratio = (1 - gs_size / original_size) * 100
                print(f"  Ghostscript: {gs_size/1024/1024:.2f} MB ({gs_ratio:.1f}% reduction)")
                print("  ✅ Ghostscript compression available")
            except Exception as e:
                print(f"  Ghostscript: Not available - {str(e)}")
                
        except Exception as e:
            print(f"❌ Error testing compression: {str(e)}")
    else:
        print(f"\n⚠️  Test file {test_file} not found")
        print("Create a test file to run compression tests")
    
    print("\n" + "=" * 50)
    print("🎯 Compression testing completed!")

def test_compression_edge_cases():
    """Test edge cases for compression"""
    print("\n🧪 Testing Compression Edge Cases")
    print("=" * 50)
    
    # Test with different quality levels
    print("\n1. Testing Different Quality Levels")
    qualities = ['low', 'medium', 'high', 'maximum']
    
    for quality in qualities:
        validation = validate_compression_settings(quality, 75)
        if validation['valid']:
            print(f"✅ {quality} quality: Valid")
        else:
            print(f"❌ {quality} quality: Invalid - {validation['errors']}")
    
    # Test with different image quality values
    print("\n2. Testing Image Quality Values")
    test_values = [1, 50, 75, 100, 0, 101, -10]
    
    for value in test_values:
        validation = validate_compression_settings('medium', value)
        if validation['valid']:
            print(f"✅ Image quality {value}: Valid")
        else:
            print(f"❌ Image quality {value}: Invalid - {validation['errors']}")
    
    print("\n" + "=" * 50)
    print("🎯 Edge case testing completed!")

def create_sample_pdf():
    """Create a sample PDF for testing"""
    print("\n📄 Creating Sample PDF for Testing")
    
    try:
        import fitz
        from io import BytesIO
        
        # Create a simple PDF
        doc = fitz.open()
        
        # Add some pages with content
        for i in range(5):
            page = doc.new_page(width=612, height=792)  # Letter size
            
            # Add some text
            text = f"This is test page {i+1} with some content to make it compressible."
            page.insert_text((72, 72), text, fontsize=12, color=(0, 0, 0))
            
            # Add a rectangle
            rect = fitz.Rect(100, 100, 500, 200)
            page.draw_rect(rect, color=(0.5, 0.5, 0.5), width=1)
        
        # Save the PDF
        sample_data = doc.save()
        doc.close()
        
        # Save to file
        os.makedirs('test_files', exist_ok=True)
        with open('test_files/sample.pdf', 'wb') as f:
            f.write(sample_data)
        
        size = len(sample_data)
        print(f"✅ Sample PDF created: test_files/sample.pdf ({size/1024:.1f} KB)")
        
    except ImportError:
        print("❌ PyMuPDF not available for creating sample PDF")
    except Exception as e:
        print(f"❌ Error creating sample PDF: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Enhanced PDF Compression Test Suite")
    print("=" * 60)
    
    # Create sample PDF if needed
    if not os.path.exists('test_files/sample.pdf'):
        create_sample_pdf()
    
    # Run tests
    test_compression_functionality()
    test_compression_edge_cases()
    
    print("\n🎉 All compression tests completed!")
    print("\nTo test with real files:")
    print("1. Place PDF files in the 'test_files' directory")
    print("2. Run: python test_compression.py")
    print("3. Check compression results and size reductions")

if __name__ == "__main__":
    main()
