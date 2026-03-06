import io
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont

def _bytesio(data: bytes) -> io.BytesIO:
    buf = io.BytesIO()
    buf.write(data)
    buf.seek(0)
    return buf

def compress_image(file_bytes: bytes, quality: int = 90) -> io.BytesIO:
    """Compress image with specified quality"""
    img = Image.open(_bytesio(file_bytes))
    
    # Convert to RGB if necessary for JPEG
    if img.mode in ('RGBA', 'LA', 'P'):
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = rgb_img
    
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=quality, optimize=True)
    out.seek(0)
    return out

def resize_image(file_bytes: bytes, width: int, height: int) -> io.BytesIO:
    """Resize image to specified dimensions"""
    img = Image.open(_bytesio(file_bytes))
    
    # Maintain aspect ratio if one dimension is 0
    if width == 0:
        ratio = height / img.height
        width = int(img.width * ratio)
    elif height == 0:
        ratio = width / img.width
        height = int(img.height * ratio)
    
    resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    out = io.BytesIO()
    resized_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def crop_image(file_bytes: bytes, x: int, y: int, width: int, height: int) -> io.BytesIO:
    """Crop image to specified area"""
    img = Image.open(_bytesio(file_bytes))
    
    # Ensure crop area is within image bounds
    x = max(0, min(x, img.width - 1))
    y = max(0, min(y, img.height - 1))
    width = min(width, img.width - x)
    height = min(height, img.height - y)
    
    cropped_img = img.crop((x, y, x + width, y + height))
    
    out = io.BytesIO()
    cropped_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def rotate_image(file_bytes: bytes, angle: int) -> io.BytesIO:
    """Rotate image by specified angle"""
    img = Image.open(_bytesio(file_bytes))
    
    # Rotate and fill with white for non-90 degree rotations
    if angle % 90 != 0:
        rotated_img = img.rotate(angle, expand=True, fillcolor='white')
    else:
        rotated_img = img.rotate(angle, expand=True)
    
    out = io.BytesIO()
    rotated_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def convert_image(file_bytes: bytes, format: str) -> io.BytesIO:
    """Convert image to specified format"""
    img = Image.open(_bytesio(file_bytes))
    
    # Handle transparency for formats that don't support it
    if format.upper() in ['JPEG', 'JPG'] and img.mode in ('RGBA', 'LA', 'P'):
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = rgb_img
    
    out = io.BytesIO()
    img.save(out, format=format)
    out.seek(0)
    return out

def flip_image(file_bytes: bytes, horizontal: bool = True) -> io.BytesIO:
    """Flip image horizontally or vertically"""
    img = Image.open(_bytesio(file_bytes))
    
    if horizontal:
        flipped_img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    else:
        flipped_img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    
    out = io.BytesIO()
    flipped_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def upscale_image(file_bytes: bytes, scale_factor: int = 2) -> io.BytesIO:
    """Upscale image by specified factor"""
    img = Image.open(_bytesio(file_bytes))
    
    new_width = img.width * scale_factor
    new_height = img.height * scale_factor
    
    upscaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    out = io.BytesIO()
    upscaled_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out
