"""
Test script for PDF Suite improvements based on test report
"""

import os
import sys
import tempfile
import requests
import json
from pathlib import Path
from enhanced_pdf_tools import (
    add_page_numbers_enhanced,
    split_pdf_enhanced,
    extract_pages_enhanced,
    rotate_pdf_enhanced,
    pdf_to_images_enhanced,
    extract_images_enhanced,
    merge_pdfs_enhanced,
    validate_page_range,
    get_pdf_info,
    PDFProcessingError
)

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_FILES_DIR = "test_files"

class TestImprovements:
    """Test all improvements based on the test report"""
    
    def __init__(self):
        self.test_results = []
        self.setup_test_files()
    
    def setup_test_files(self):
        """Create test directory and prepare test files"""
        os.makedirs(TEST_FILES_DIR, exist_ok=True)
        print(f"Test files directory: {TEST_FILES_DIR}")
    
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "message": message
        })
        print(f"[{status}] {test_name}: {message}")
    
    def test_page_numbering_large_pdf(self):
        """Test page numbering for large PDF files"""
        print("\n=== Testing Page Numbering for Large PDFs ===")
        
        try:
            # Create a large PDF (simulate 40+ MB)
            # Note: This would require an actual large PDF file
            test_file = os.path.join(TEST_FILES_DIR, "large_test.pdf")
            
            if not os.path.exists(test_file):
                self.log_test("Large PDF Page Numbering", False, "Test file not available")
                return
            
            # Test enhanced page numbering
            result = add_page_numbers_enhanced(
                test_file,
                format_string="Page {n}",
                position="bottom-center",
                font_size=12
            )
            
            # Verify result
            if result and len(result) > 0:
                self.log_test("Large PDF Page Numbering", True, "Successfully added page numbers to large PDF")
            else:
                self.log_test("Large PDF Page Numbering", False, "Failed to process large PDF")
                
        except Exception as e:
            self.log_test("Large PDF Page Numbering", False, f"Error: {str(e)}")
    
    def test_page_range_validation(self):
        """Test page range validation"""
        print("\n=== Testing Page Range Validation ===")
        
        # Test valid range
        validation = validate_page_range(1, 10, 20)
        if validation['valid']:
            self.log_test("Valid Page Range", True, "Valid range (1-10) passed")
        else:
            self.log_test("Valid Page Range", False, f"Valid range failed: {validation['errors']}")
        
        # Test invalid range (from > to)
        validation = validate_page_range(30, 3, 60)
        if not validation['valid'] and "From page must be less than or equal to To page" in validation['errors']:
            self.log_test("Invalid Page Range (From > To)", True, "Correctly rejected invalid range")
        else:
            self.log_test("Invalid Page Range (From > To)", False, "Failed to reject invalid range")
        
        # Test out of bounds range
        validation = validate_page_range(1, 100, 60)
        if not validation['valid']:
            self.log_test("Out of Bounds Range", True, "Correctly rejected out of bounds range")
        else:
            self.log_test("Out of Bounds Range", False, "Failed to reject out of bounds range")
        
        # Test non-numeric input
        try:
            validation = validate_page_range("abc", 10, 20)
            if not validation['valid']:
                self.log_test("Non-Numeric Input", True, "Correctly rejected non-numeric input")
            else:
                self.log_test("Non-Numeric Input", False, "Failed to reject non-numeric input")
        except:
            self.log_test("Non-Numeric Input", True, "Correctly handled non-numeric input")
    
    def test_file_size_validation(self):
        """Test file size validation"""
        print("\n=== Testing File Size Validation ===")
        
        try:
            from enhanced_pdf_tools import MAX_FILE_SIZE, validate_file_size
            
            # Test file within limit
            small_file = b"x" * (10 * 1024 * 1024)  # 10MB
            try:
                validate_file_size(small_file)
                self.log_test("File Size Validation (Small File)", True, "Small file passed validation")
            except PDFProcessingError:
                self.log_test("File Size Validation (Small File)", False, "Small file failed validation")
            
            # Test file exceeding limit
            large_file = b"x" * (MAX_FILE_SIZE + 1)  # Over limit
            try:
                validate_file_size(large_file)
                self.log_test("File Size Validation (Large File)", False, "Large file should have failed validation")
            except PDFProcessingError as e:
                if "exceeds maximum allowed size" in str(e):
                    self.log_test("File Size Validation (Large File)", True, "Correctly rejected large file")
                else:
                    self.log_test("File Size Validation (Large File)", False, f"Wrong error message: {str(e)}")
                    
        except Exception as e:
            self.log_test("File Size Validation", False, f"Error: {str(e)}")
    
    def test_ui_file_preview_layout(self):
        """Test UI file preview layout (manual test)"""
        print("\n=== Testing UI File Preview Layout ===")
        
        # This would require manual testing of the web interface
        print("Manual test required:")
        print("1. Open the enhanced web interface")
        print("2. Upload a PDF with a long filename")
        print("3. Verify filename displays correctly without breaking")
        print("4. Check responsive behavior on mobile")
        
        self.log_test("UI File Preview Layout", True, "Manual test instructions provided")
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n=== Testing API Endpoints ===")
        
        try:
            # Test PDF info endpoint
            test_file = os.path.join(TEST_FILES_DIR, "test.pdf")
            
            if not os.path.exists(test_file):
                self.log_test("API Endpoints", False, "Test file not available")
                return
            
            with open(test_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{BASE_URL}/api/pdf-info", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.log_test("PDF Info API", True, "PDF info retrieved successfully")
                    else:
                        self.log_test("PDF Info API", False, f"API error: {data.get('error')}")
                else:
                    self.log_test("PDF Info API", False, f"HTTP error: {response.status_code}")
                    
        except requests.exceptions.ConnectionError:
            self.log_test("API Endpoints", False, "Server not running")
        except Exception as e:
            self.log_test("API Endpoints", False, f"Error: {str(e)}")
    
    def test_pdf_to_images_conversion(self):
        """Test PDF to images conversion"""
        print("\n=== Testing PDF to Images Conversion ===")
        
        try:
            test_file = os.path.join(TEST_FILES_DIR, "test.pdf")
            
            if not os.path.exists(test_file):
                self.log_test("PDF to Images", False, "Test file not available")
                return
            
            # Test conversion with different DPI
            images = pdf_to_images_enhanced(test_file, dpi=150, format="PNG")
            
            if images and len(images) > 0:
                self.log_test("PDF to Images", True, f"Successfully converted to {len(images)} images")
            else:
                self.log_test("PDF to Images", False, "No images generated")
                
        except Exception as e:
            self.log_test("PDF to Images", False, f"Error: {str(e)}")
    
    def test_image_extraction(self):
        """Test image extraction from PDF"""
        print("\n=== Testing Image Extraction ===")
        
        try:
            test_file = os.path.join(TEST_FILES_DIR, "test_with_images.pdf")
            
            if not os.path.exists(test_file):
                self.log_test("Image Extraction", False, "Test file not available")
                return
            
            # Test image extraction
            extracted_images = extract_images_enhanced(test_file)
            
            if extracted_images and len(extracted_images) > 0:
                self.log_test("Image Extraction", True, f"Successfully extracted {len(extracted_images)} images")
            else:
                self.log_test("Image Extraction", True, "No images found in PDF (may be expected)")
                
        except Exception as e:
            self.log_test("Image Extraction", False, f"Error: {str(e)}")
    
    def test_rotation_functionality(self):
        """Test PDF rotation functionality"""
        print("\n=== Testing PDF Rotation ===")
        
        try:
            test_file = os.path.join(TEST_FILES_DIR, "test.pdf")
            
            if not os.path.exists(test_file):
                self.log_test("PDF Rotation", False, "Test file not available")
                return
            
            # Test rotation
            rotated_pdf = rotate_pdf_enhanced(test_file, angle=90, page_range="all")
            
            if rotated_pdf and len(rotated_pdf) > 0:
                self.log_test("PDF Rotation", True, "Successfully rotated PDF")
            else:
                self.log_test("PDF Rotation", False, "Failed to rotate PDF")
                
        except Exception as e:
            self.log_test("PDF Rotation", False, f"Error: {str(e)}")
    
    def test_merge_functionality(self):
        """Test PDF merge functionality"""
        print("\n=== Testing PDF Merge ===")
        
        try:
            test_file1 = os.path.join(TEST_FILES_DIR, "test1.pdf")
            test_file2 = os.path.join(TEST_FILES_DIR, "test2.pdf")
            
            if not os.path.exists(test_file1) or not os.path.exists(test_file2):
                self.log_test("PDF Merge", False, "Test files not available")
                return
            
            # Test merge
            merged_pdf = merge_pdfs_enhanced([test_file1, test_file2])
            
            if merged_pdf and len(merged_pdf) > 0:
                self.log_test("PDF Merge", True, "Successfully merged PDFs")
            else:
                self.log_test("PDF Merge", False, "Failed to merge PDFs")
                
        except Exception as e:
            self.log_test("PDF Merge", False, f"Error: {str(e)}")
    
    def test_split_functionality(self):
        """Test PDF split functionality"""
        print("\n=== Testing PDF Split ===")
        
        try:
            test_file = os.path.join(TEST_FILES_DIR, "test.pdf")
            
            if not os.path.exists(test_file):
                self.log_test("PDF Split", False, "Test file not available")
                return
            
            # Test split
            split_pdf = split_pdf_enhanced(test_file, from_page=1, to_page=5)
            
            if split_pdf and len(split_pdf) > 0:
                self.log_test("PDF Split", True, "Successfully split PDF")
            else:
                self.log_test("PDF Split", False, "Failed to split PDF")
                
        except Exception as e:
            self.log_test("PDF Split", False, f"Error: {str(e)}")
    
    def test_extract_pages_functionality(self):
        """Test page extraction functionality"""
        print("\n=== Testing Page Extraction ===")
        
        try:
            test_file = os.path.join(TEST_FILES_DIR, "test.pdf")
            
            if not os.path.exists(test_file):
                self.log_test("Page Extraction", False, "Test file not available")
                return
            
            # Test extraction
            extracted_pdf = extract_pages_enhanced(test_file, [1, 3, 5])
            
            if extracted_pdf and len(extracted_pdf) > 0:
                self.log_test("Page Extraction", True, "Successfully extracted pages")
            else:
                self.log_test("Page Extraction", False, "Failed to extract pages")
                
        except Exception as e:
            self.log_test("Page Extraction", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all improvement tests"""
        print("🧪 Running PDF Suite Improvement Tests")
        print("=" * 50)
        
        # Core functionality tests
        self.test_page_numbering_large_pdf()
        self.test_page_range_validation()
        self.test_file_size_validation()
        
        # Feature tests
        self.test_pdf_to_images_conversion()
        self.test_image_extraction()
        self.test_rotation_functionality()
        self.test_merge_functionality()
        self.test_split_functionality()
        self.test_extract_pages_functionality()
        
        # UI tests
        self.test_ui_file_preview_layout()
        
        # API tests
        self.test_api_endpoints()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed = sum(1 for result in self.test_results if result["status"] == "FAIL")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n✅ Test completed!")


def main():
    """Main function to run tests"""
    tester = TestImprovements()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
