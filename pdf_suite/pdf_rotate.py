"""
PDF Rotate Tool - Rotate PDF pages by specified angles
"""

import io
import os
from typing import Union, List
from PyMuPDF import fitz

def rotate_pdf(pdf_file: Union[str, bytes], 
               angle: int = 90,
               page_range: str = "all",
               output_path: str = None) -> bytes:
    """
    Rotate PDF pages by specified angle
    
    Args:
        pdf_file: PDF file path or bytes
        angle: Rotation angle (90, 180, 270, or custom)
        page_range: Page range like "1-5" or "all"
        output_path: Optional output file path
    
    Returns:
        bytes: Rotated PDF data
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            if not os.path.exists(pdf_file):
                raise FileNotFoundError(f"PDF file not found: {pdf_file}")
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Determine which pages to rotate
        pages_to_rotate = _get_pages_to_rotate(pdf_doc, page_range)
        
        # Rotate specified pages
        for page_num in pages_to_rotate:
            page = pdf_doc[page_num]
            page.set_rotation(angle)
        
        # Save rotated PDF
        rotated_bytes = pdf_doc.write()
        pdf_doc.close()
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(rotated_bytes)
        
        return rotated_bytes
        
    except Exception as e:
        raise ValueError(f"Error rotating PDF: {str(e)}")

def rotate_pdf_multiple_angles(pdf_file: Union[str, bytes],
                          rotation_config: List[dict],
                          output_path: str = None) -> bytes:
    """
    Rotate different pages by different angles
    
    Args:
        pdf_file: PDF file path or bytes
        rotation_config: List of {'pages': str, 'angle': int} dictionaries
        output_path: Optional output file path
    
    Returns:
        bytes: Rotated PDF data
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Apply different rotations to different page ranges
        for config in rotation_config:
            pages_to_rotate = _get_pages_to_rotate(pdf_doc, config['pages'])
            angle = config['angle']
            
            for page_num in pages_to_rotate:
                page = pdf_doc[page_num]
                page.set_rotation(angle)
        
        # Save rotated PDF
        rotated_bytes = pdf_doc.write()
        pdf_doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(rotated_bytes)
        
        return rotated_bytes
        
    except Exception as e:
        raise ValueError(f"Error rotating PDF with multiple angles: {str(e)}")

def auto_rotate_pdf(pdf_file: Union[str, bytes],
                 output_path: str = None) -> bytes:
    """
    Automatically rotate pages to correct orientation
    
    Args:
        pdf_file: PDF file path or bytes
        output_path: Optional output file path
    
    Returns:
        bytes: Auto-rotated PDF data
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Auto-rotate each page based on content
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            
            # Get page dimensions
            rect = page.rect
            width, height = rect.width, rect.height
            
            # Determine if page needs rotation
            # This is a simple heuristic - you might want more sophisticated analysis
            if width > height * 1.5:  # Likely landscape that should be portrait
                page.set_rotation(90)
            elif height > width * 1.5:  # Likely portrait that should be landscape
                page.set_rotation(0)
            # Otherwise, keep current rotation
        
        # Save auto-rotated PDF
        rotated_bytes = pdf_doc.write()
        pdf_doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(rotated_bytes)
        
        return rotated_bytes
        
    except Exception as e:
        raise ValueError(f"Error auto-rotating PDF: {str(e)}")

def _get_pages_to_rotate(pdf_doc, page_range: str) -> List[int]:
    """
    Get list of page indices to rotate based on page range
    
    Args:
        pdf_doc: PyMuPDF document
        page_range: Page range string
    
    Returns:
        List[int]: Page indices (0-based)
    """
    total_pages = len(pdf_doc)
    
    if page_range.lower() == "all":
        return list(range(total_pages))
    
    # Parse page range (1-based to 0-based)
    pages = []
    for part in page_range.split(','):
        part = part.strip()
        
        if '-' in part:
            # Range like "1-5"
            start, end = part.split('-')
            try:
                start = max(1, int(start.strip()))
                end = min(total_pages, int(end.strip()))
                pages.extend(range(start - 1, end))  # Convert to 0-based
            except ValueError:
                print(f"Invalid range: {part}")
        else:
            # Single page like "7"
            try:
                page = int(part)
                if 1 <= page <= total_pages:
                    pages.append(page - 1)  # Convert to 0-based
            except ValueError:
                print(f"Invalid page: {part}")
    
    return sorted(list(set(pages)))  # Remove duplicates and sort

def get_rotation_info(pdf_file: Union[str, bytes]) -> dict:
    """
    Get rotation information for all pages
    
    Args:
        pdf_file: PDF file path or bytes
    
    Returns:
        dict: Rotation information
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        rotation_info = {
            'total_pages': len(pdf_doc),
            'pages': []
        }
        
        # Get rotation for each page
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            rect = page.rect
            
            rotation_info['pages'].append({
                'page': page_num + 1,
                'rotation': page.rotation,
                'width': rect.width,
                'height': rect.height,
                'orientation': 'landscape' if rect.width > rect.height else 'portrait'
            })
        
        pdf_doc.close()
        return rotation_info
        
    except Exception as e:
        raise ValueError(f"Error getting rotation info: {str(e)}")

def normalize_rotation(angle: int) -> int:
    """
    Normalize rotation angle to standard values
    
    Args:
        angle: Rotation angle
    
    Returns:
        int: Normalized angle (0, 90, 180, 270)
    """
    # Normalize to 0-360 range
    angle = angle % 360
    
    # Round to nearest standard rotation
    if angle < 45 or angle >= 315:
        return 0
    elif angle < 135:
        return 90
    elif angle < 225:
        return 180
    else:
        return 270

# Example usage and testing
if __name__ == "__main__":
    # Test rotate functionality
    test_file = "test.pdf"  # Replace with actual test file
    
    try:
        # Test simple rotation
        rotated = rotate_pdf(test_file, 90, "all", "rotated_90.pdf")
        print("PDF rotated 90 degrees successfully!")
        
        # Test range rotation
        rotated_range = rotate_pdf(test_file, 180, "1-3", "rotated_range.pdf")
        print("PDF pages 1-3 rotated 180 degrees!")
        
        # Test auto-rotation
        auto_rotated = auto_rotate_pdf(test_file, "auto_rotated.pdf")
        print("PDF auto-rotated successfully!")
        
        # Get rotation info
        info = get_rotation_info(test_file)
        print(f"Rotation info: {info}")
        
    except Exception as e:
        print(f"Error during rotation: {str(e)}")
