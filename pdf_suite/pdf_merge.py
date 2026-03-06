"""
PDF Merge Tool - Combine multiple PDFs into one document
"""

import io
import os
from typing import List, Union
from PyMuPDF import fitz

def merge_pdfs(pdf_files: List[Union[str, bytes]], output_path: str = None) -> bytes:
    """
    Merge multiple PDF files into a single PDF
    
    Args:
        pdf_files: List of PDF file paths or bytes
        output_path: Optional output file path
    
    Returns:
        bytes: Merged PDF data
    """
    if not pdf_files:
        raise ValueError("No PDF files provided")
    
    # Create new PDF document
    merged_pdf = fitz.open()
    
    for pdf_file in pdf_files:
        try:
            # Handle both file paths and bytes
            if isinstance(pdf_file, str):
                if not os.path.exists(pdf_file):
                    raise FileNotFoundError(f"PDF file not found: {pdf_file}")
                pdf_doc = fitz.open(pdf_file)
            else:
                pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
            
            # Insert all pages from current PDF
            merged_pdf.insert_pdf(pdf_doc)
            pdf_doc.close()
            
        except Exception as e:
            print(f"Error processing PDF {pdf_file}: {str(e)}")
            continue
    
    # Save merged PDF
    merged_bytes = merged_pdf.write()
    merged_pdf.close()
    
    # Save to file if path provided
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(merged_bytes)
    
    return merged_bytes

def merge_pdfs_with_metadata(pdf_files: List[Union[str, bytes]], 
                          output_path: str = None,
                          title: str = "Merged Document",
                          author: str = "PDF Merger",
                          subject: str = "Merged PDF Document") -> bytes:
    """
    Merge PDFs with custom metadata
    
    Args:
        pdf_files: List of PDF file paths or bytes
        output_path: Optional output file path
        title: Document title
        author: Document author
        subject: Document subject
    
    Returns:
        bytes: Merged PDF data with metadata
    """
    merged_bytes = merge_pdfs(pdf_files)
    
    # Add metadata to merged PDF
    pdf_doc = fitz.open(stream=merged_bytes, filetype="pdf")
    metadata = {
        "title": title,
        "author": author,
        "subject": subject,
        "creator": "New00 PDF Merger",
        "producer": "PyMuPDF"
    }
    
    pdf_doc.set_metadata(metadata)
    
    # Save with metadata
    final_bytes = pdf_doc.write()
    pdf_doc.close()
    
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(final_bytes)
    
    return final_bytes

def get_pdf_page_count(pdf_file: Union[str, bytes]) -> int:
    """
    Get the number of pages in a PDF
    
    Args:
        pdf_file: PDF file path or bytes
    
    Returns:
        int: Number of pages
    """
    try:
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        page_count = len(pdf_doc)
        pdf_doc.close()
        return page_count
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")

def validate_pdf_files(pdf_files: List[Union[str, bytes]]) -> List[Union[str, bytes]]:
    """
    Validate that all provided files are valid PDFs
    
    Args:
        pdf_files: List of file paths or bytes
    
    Returns:
        List: Valid PDF files only
    """
    valid_files = []
    
    for pdf_file in pdf_files:
        try:
            if isinstance(pdf_file, str):
                if not os.path.exists(pdf_file):
                    print(f"File not found: {pdf_file}")
                    continue
                
                # Check file extension
                if not pdf_file.lower().endswith('.pdf'):
                    print(f"Not a PDF file: {pdf_file}")
                    continue
            
            # Try to open PDF to validate
            if isinstance(pdf_file, str):
                pdf_doc = fitz.open(pdf_file)
            else:
                pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
            
            pdf_doc.close()
            valid_files.append(pdf_file)
            
        except Exception as e:
            print(f"Invalid PDF file {pdf_file}: {str(e)}")
            continue
    
    return valid_files

# Example usage and testing
if __name__ == "__main__":
    # Test merge functionality
    test_files = ["test1.pdf", "test2.pdf"]  # Replace with actual test files
    
    try:
        merged = merge_pdfs(test_files, "merged_output.pdf")
        print("PDF merge completed successfully!")
        print(f"Output size: {len(merged)} bytes")
    except Exception as e:
        print(f"Error during merge: {str(e)}")
