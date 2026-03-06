import io
import zipfile
from PIL import Image
from tools.basic_tools import compress_image, resize_image, convert_image
from tools.adjustments import adjust_brightness, adjust_contrast, adjust_saturation
from tools.effects import blur_image, sharpen_image, grayscale_image, sepia_image, invert_image
from tools.watermark import add_watermark

def _bytesio(data: bytes) -> io.BytesIO:
    buf = io.BytesIO()
    buf.write(data)
    buf.seek(0)
    return buf

def batch_process_images(files, operation, **kwargs):
    """Process multiple images with specified operation"""
    processed_files = []
    
    for file_data in files:
        if isinstance(file_data, bytes):
            file_bytes = file_data
        else:
            # Handle file upload objects
            file_bytes = file_data.read()
        
        try:
            if operation == 'compress':
                quality = kwargs.get('quality', 90)
                result = compress_image(file_bytes, quality)
            elif operation == 'resize':
                width = kwargs.get('width', 800)
                height = kwargs.get('height', 600)
                result = resize_image(file_bytes, width, height)
            elif operation == 'convert':
                format = kwargs.get('format', 'JPEG')
                result = convert_image(file_bytes, format)
            elif operation == 'brightness':
                factor = kwargs.get('factor', 1.2)
                result = adjust_brightness(file_bytes, factor)
            elif operation == 'contrast':
                factor = kwargs.get('factor', 1.2)
                result = adjust_contrast(file_bytes, factor)
            elif operation == 'saturation':
                factor = kwargs.get('factor', 1.2)
                result = adjust_saturation(file_bytes, factor)
            elif operation == 'blur':
                radius = kwargs.get('radius', 2.0)
                result = blur_image(file_bytes, radius)
            elif operation == 'sharpen':
                result = sharpen_image(file_bytes)
            elif operation == 'grayscale':
                result = grayscale_image(file_bytes)
            elif operation == 'sepia':
                result = sepia_image(file_bytes)
            elif operation == 'invert':
                result = invert_image(file_bytes)
            elif operation == 'watermark':
                text = kwargs.get('text', '© Watermark')
                position = kwargs.get('position', 'bottom-right')
                result = add_watermark(file_bytes, text, position)
            else:
                # Default to original if operation not recognized
                result = _bytesio(file_bytes)
            
            processed_files.append(result.getvalue())
            
        except Exception as e:
            # If processing fails, include original file
            processed_files.append(file_bytes)
    
    # Create ZIP file with processed images
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, processed_data in enumerate(processed_files):
            zip_file.writestr(f"processed_image_{i+1}.jpg", processed_data)
    
    zip_buffer.seek(0)
    return zip_buffer
