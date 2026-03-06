"""
PDF Split Tool - Split PDF into individual pages or ranges
"""

import io
import os
from typing import List, Union, Tuple
from PyMuPDF import fitz

def split_pdf_each_page(pdf_file: Union[str, bytes], 
                     output_dir: str = "split_output") -> List[bytes]:
    """
    Split PDF into individual pages
    
    Args:
        pdf_file: PDF file path or bytes
        output_dir: Directory to save split pages
    
    Returns:
        List[bytes]: Individual page data
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            if not os.path.exists(pdf_file):
                raise FileNotFoundError(f"PDF file not found: {pdf_file}")
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        split_pages = []
        
        # Split each page
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            
            # Create new PDF with single page
            new_pdf = fitz.open()
            new_pdf.insert_pdf(pdf_doc, from_page=page_num, to_page=page_num)
            
            # Save page
            page_bytes = new_pdf.write()
            split_pages.append(page_bytes)
            
            # Save to file
            output_path = os.path.join(output_dir, f"page_{page_num + 1:03d}.pdf")
            with open(output_path, 'wb') as f:
                f.write(page_bytes)
            
            new_pdf.close()
        
        pdf_doc.close()
        return split_pages
        
    except Exception as e:
        raise ValueError(f"Error splitting PDF: {str(e)}")

def split_pdf_range(pdf_file: Union[str, bytes], 
                  page_ranges: List[Tuple[int, int]],
                  output_dir: str = "split_output") -> List[bytes]:
    """
    Split PDF by page ranges
    
    Args:
        pdf_file: PDF file path or bytes
        page_ranges: List of (start, end) tuples (1-based, inclusive)
        output_dir: Directory to save split PDFs
    
    Returns:
        List[bytes]: Split PDF data
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        split_pdfs = []
        
        for i, (start, end) in enumerate(page_ranges):
            # Validate page range
            if start < 1 or end > len(pdf_doc) or start > end:
                print(f"Invalid page range: {start}-{end}")
                continue
            
            # Convert to 0-based indexing
            start_idx = start - 1
            end_idx = end - 1
            
            # Create new PDF with specified range
            new_pdf = fitz.open()
            new_pdf.insert_pdf(pdf_doc, from_page=start_idx, to_page=end_idx)
            
            # Save range
            range_bytes = new_pdf.write()
            split_pdfs.append(range_bytes)
            
            # Save to file
            output_path = os.path.join(output_dir, f"pages_{start}-{end}.pdf")
            with open(output_path, 'wb') as f:
                f.write(range_bytes)
            
            new_pdf.close()
        
        pdf_doc.close()
        return split_pdfs
        
    except Exception as e:
        raise ValueError(f"Error splitting PDF by range: {str(e)}")

def split_pdf_by_chunks(pdf_file: Union[str, bytes], 
                      chunk_size: int,
                      output_dir: str = "split_output") -> List[bytes]:
    """
    Split PDF into chunks of specified size
    
    Args:
        pdf_file: PDF file path or bytes
        chunk_size: Number of pages per chunk
        output_dir: Directory to save chunks
    
    Returns:
        List[bytes]: Chunk PDF data
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        total_pages = len(pdf_doc)
        chunks = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Split into chunks
        for chunk_start in range(0, total_pages, chunk_size):
            chunk_end = min(chunk_start + chunk_size - 1, total_pages - 1)
            
            # Create new PDF for chunk
            new_pdf = fitz.open()
            new_pdf.insert_pdf(pdf_doc, from_page=chunk_start, to_page=chunk_end)
            
            # Save chunk
            chunk_bytes = new_pdf.write()
            chunks.append(chunk_bytes)
            
            # Save to file
            chunk_num = chunk_start // chunk_size + 1
            output_path = os.path.join(output_dir, f"chunk_{chunk_num}_pages_{chunk_start+1}-{chunk_end+1}.pdf")
            with open(output_path, 'wb') as f:
                f.write(chunk_bytes)
            
            new_pdf.close()
        
        pdf_doc.close()
        return chunks
        
    except Exception as e:
        raise ValueError(f"Error splitting PDF by chunks: {str(e)}")

def parse_page_ranges(range_string: str) -> List[Tuple[int, int]]:
    """
    Parse page range string into list of tuples
    
    Args:
        range_string: String like "1-5,7,9-12"
    
    Returns:
        List[Tuple[int, int]]: List of (start, end) tuples
    """
    ranges = []
    
    for part in range_string.split(','):
        part = part.strip()
        
        if '-' in part:
            # Range like "1-5"
            start, end = part.split('-')
            try:
                start = int(start.strip())
                end = int(end.strip())
                ranges.append((start, end))
            except ValueError:
                print(f"Invalid range: {part}")
        else:
            # Single page like "7"
            try:
                page = int(part)
                ranges.append((page, page))
            except ValueError:
                print(f"Invalid page: {part}")
    
    return ranges

def extract_page_info(pdf_file: Union[str, bytes]) -> dict:
    """
    Extract information about PDF pages
    
    Args:
        pdf_file: PDF file path or bytes
    
    Returns:
        dict: Page information
    """
    try:
        # Open PDF document
        if isinstance(pdf_file, str):
            pdf_doc = fitz.open(pdf_file)
        else:
            pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        page_info = {
            'total_pages': len(pdf_doc),
            'page_sizes': [],
            'page_info': []
        }
        
        # Get information for each page
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            rect = page.rect
            page_info['page_sizes'].append({
                'page': page_num + 1,
                'width': rect.width,
                'height': rect.height,
                'orientation': 'landscape' if rect.width > rect.height else 'portrait'
            })
        
        pdf_doc.close()
        return page_info
        
    except Exception as e:
        raise ValueError(f"Error extracting page info: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    # Test split functionality
    test_file = "test.pdf"  # Replace with actual test file
    
    try:
        # Test individual page split
        pages = split_pdf_each_page(test_file)
        print(f"Split into {len(pages)} individual pages")
        
        # Test range split
        ranges = [(1, 3), (5, 7)]
        range_splits = split_pdf_range(test_file, ranges)
        print(f"Split into {len(range_splits)} ranges")
        
        # Test chunk split
        chunks = split_pdf_by_chunks(test_file, 5)
        print(f"Split into {len(chunks)} chunks")
        
    except Exception as e:
        print(f"Error during split: {str(e)}")
