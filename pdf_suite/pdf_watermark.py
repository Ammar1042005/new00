"""
PDF Watermark Tool - Add text or image watermarks to PDFs
"""

import io
import os
from typing import Union, Tuple, Optional
from PyMuPDF import fitz

def add_text_watermark(pdf_file: Union[str, bytes],
                     text: str = "CONFIDENTIAL",
                     position: str = "center",
                     font_size: int = 50,
                     color: Tuple[int, int, int] = (128, 128, 128),
                     opacity: float = 0.5,
                     rotation: int = 45,
                     output_path: str = None) -> bytes:
    """
    Add text watermark to PDF
    
    Args:
        pdf_file: PDF file path or bytes
        text: Watermark text
        position: Position (center, top-left, top-right, bottom-left, bottom-right)
        font_size: Font size for watermark text
        color: RGB color tuple (0-255)
        opacity: Transparency (0.0 to 1.0)
        rotation: Rotation angle in degrees
        output_path: Optional output file path
    
    Returns:
        bytes: Watermarked PDF data
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            if not os.path.exists(pdf_file):
                raise FileNotFoundError(f"PDF file not found: {pdf_file}")
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Process each page
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            rect = page.rect
            
            # Calculate watermark position
            x, y = _calculate_watermark_position(rect, position, text, font_size)
            
            # Create watermark text
            text_rect = fitz.Rect(x, y, x + 300, y + 100)  # Approximate text bounds
            
            # Add watermark to page
            page.insert_text(
                (x, y),
                text,
                fontsize=font_size,
                color=color,
                opacity=opacity,
                rotate=rotation,
                fontname="helv"
            )
        
        # Save watermarked PDF
        watermarked_bytes = pdf_doc.write()
        pdf_doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(watermarked_bytes)
        
        return watermarked_bytes
        
    except Exception as e:
        raise ValueError(f"Error adding text watermark: {str(e)}")

def add_image_watermark(pdf_file: Union[str, bytes],
                      watermark_image: Union[str, bytes],
                      position: str = "center",
                      opacity: float = 0.3,
                      scale: float = 0.2,
                      output_path: str = None) -> bytes:
    """
    Add image watermark to PDF
    
    Args:
        pdf_file: PDF file path or bytes
        watermark_image: Watermark image path or bytes
        position: Position (center, top-left, etc.)
        opacity: Transparency (0.0 to 1.0)
        scale: Scale factor for watermark image
        output_path: Optional output file path
    
    Returns:
        bytes: Watermarked PDF data
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Load watermark image
        if isinstance(watermark_image, str):
            if not os.path.exists(watermark_image):
                raise FileNotFoundError(f"Watermark image not found: {watermark_image}")
            watermark_img = fitz.Pixmap(watermark_image)
        else:
            watermark_img = fitz.Pixmap(watermark_image)
        
        # Process each page
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            rect = page.rect
            
            # Calculate watermark position and size
            wm_width = int(rect.width * scale)
            wm_height = int(watermark_img.height * (wm_width / watermark_img.width))
            
            x, y = _calculate_image_position(rect, position, wm_width, wm_height)
            
            # Create image rectangle
            img_rect = fitz.Rect(x, y, x + wm_width, y + wm_height)
            
            # Add watermark to page (as overlay)
            page.insert_image(img_rect, watermark_img, overlay=True)
        
        # Save watermarked PDF
        watermarked_bytes = pdf_doc.write()
        pdf_doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(watermarked_bytes)
        
        return watermarked_bytes
        
    except Exception as e:
        raise ValueError(f"Error adding image watermark: {str(e)}")

def add_page_numbers(pdf_file: Union[str, bytes],
                   format_string: str = "Page {n}",
                   position: str = "bottom-center",
                   font_size: int = 12,
                   color: Tuple[int, int, int] = (0, 0, 0),
                   start_page: int = 1,
                   output_path: str = None) -> bytes:
    """
    Add page numbers to PDF
    
    Args:
        pdf_file: PDF file path or bytes
        format_string: Format string for page numbers
        position: Position (bottom-center, top-right, etc.)
        font_size: Font size for page numbers
        color: RGB color tuple
        start_page: Starting page number
        output_path: Optional output file path
    
    Returns:
        bytes: PDF with page numbers
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Process each page
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            rect = page.rect
            
            # Calculate page number position
            x, y = _calculate_page_number_position(rect, position, font_size)
            
            # Format page number
            page_text = format_string.format(n=page_num + start_page)
            
            # Add page number to page
            page.insert_text(
                (x, y),
                page_text,
                fontsize=font_size,
                color=color,
                fontname="helv"
            )
        
        # Save PDF with page numbers
        numbered_bytes = pdf_doc.write()
        pdf_doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(numbered_bytes)
        
        return numbered_bytes
        
    except Exception as e:
        raise ValueError(f"Error adding page numbers: {str(e)}")

def add_header_footer(pdf_file: Union[str, bytes],
                   header_text: str = "",
                   footer_text: str = "",
                   font_size: int = 10,
                   color: Tuple[int, int, int] = (0, 0, 0),
                   output_path: str = None) -> bytes:
    """
    Add header and footer to PDF
    
    Args:
        pdf_file: PDF file path or bytes
        header_text: Text to add to header
        footer_text: Text to add to footer
        font_size: Font size for header/footer
        color: RGB color tuple
        output_path: Optional output file path
    
    Returns:
        bytes: PDF with header and footer
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Process each page
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            rect = page.rect
            
            # Add header
            if header_text:
                header_x = rect.width / 2
                header_y = 20
                page.insert_text(
                    (header_x, header_y),
                    header_text,
                    fontsize=font_size,
                    color=color,
                    fontname="helv",
                    align=fitz.TEXT_ALIGN_CENTER
                )
            
            # Add footer
            if footer_text:
                footer_x = rect.width / 2
                footer_y = rect.height - 20
                page.insert_text(
                    (footer_x, footer_y),
                    footer_text,
                    fontsize=font_size,
                    color=color,
                    fontname="helv",
                    align=fitz.TEXT_ALIGN_CENTER
                )
        
        # Save PDF with header and footer
        hf_bytes = pdf_doc.write()
        pdf_doc.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(hf_bytes)
        
        return hf_bytes
        
    except Exception as e:
        raise ValueError(f"Error adding header/footer: {str(e)}")

def _calculate_watermark_position(rect, position: str, text: str, font_size: int) -> Tuple[float, float]:
    """Calculate watermark position based on page rectangle"""
    width, height = rect.width, rect.height
    
    if position == "center":
        return (width / 2 - len(text) * font_size / 4, height / 2)
    elif position == "top-left":
        return (50, 50)
    elif position == "top-right":
        return (width - 200, 50)
    elif position == "bottom-left":
        return (50, height - 100)
    elif position == "bottom-right":
        return (width - 200, height - 100)
    else:
        return (width / 2, height / 2)  # Default to center

def _calculate_image_position(rect, position: str, img_width: int, img_height: int) -> Tuple[float, float]:
    """Calculate image watermark position"""
    width, height = rect.width, rect.height
    
    if position == "center":
        return ((width - img_width) / 2, (height - img_height) / 2)
    elif position == "top-left":
        return (50, 50)
    elif position == "top-right":
        return (width - img_width - 50, 50)
    elif position == "bottom-left":
        return (50, height - img_height - 50)
    elif position == "bottom-right":
        return (width - img_width - 50, height - img_height - 50)
    else:
        return ((width - img_width) / 2, (height - img_height) / 2)

def _calculate_page_number_position(rect, position: str, font_size: int) -> Tuple[float, float]:
    """Calculate page number position"""
    width, height = rect.width, rect.height
    margin = 20
    
    if position == "bottom-center":
        return (width / 2, height - margin)
    elif position == "bottom-left":
        return (margin, height - margin)
    elif position == "bottom-right":
        return (width - margin - 50, height - margin)
    elif position == "top-center":
        return (width / 2, margin)
    elif position == "top-left":
        return (margin, margin)
    elif position == "top-right":
        return (width - margin - 50, margin)
    else:
        return (width / 2, height - margin)  # Default to bottom-center

# Example usage and testing
if __name__ == "__main__":
    # Test watermark functionality
    test_file = "test.pdf"  # Replace with actual test file
    
    try:
        # Test text watermark
        watermarked = add_text_watermark(
            test_file, 
            "CONFIDENTIAL", 
            "center", 
            50, 
            (128, 128, 128), 
            0.5, 
            45,
            "watermarked.pdf"
        )
        print("Text watermark added successfully!")
        
        # Test page numbers
        numbered = add_page_numbers(
            test_file,
            "Page {n} of {total}",
            "bottom-center",
            12,
            (0, 0, 0),
            1,
            "numbered.pdf"
        )
        print("Page numbers added successfully!")
        
        # Test header/footer
        hf = add_header_footer(
            test_file,
            "Confidential Document",
            "© 2024 Your Company",
            10,
            (0, 0, 0),
            "header_footer.pdf"
        )
        print("Header and footer added successfully!")
        
    except Exception as e:
        print(f"Error during watermarking: {str(e)}")
