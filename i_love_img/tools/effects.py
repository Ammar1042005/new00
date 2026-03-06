import io
from PIL import Image, ImageFilter, ImageEnhance

def _bytesio(data: bytes) -> io.BytesIO:
    buf = io.BytesIO()
    buf.write(data)
    buf.seek(0)
    return buf

def blur_image(file_bytes: bytes, radius: float = 2.0) -> io.BytesIO:
    """Apply blur effect to image"""
    img = Image.open(_bytesio(file_bytes))
    blurred_img = img.filter(ImageFilter.GaussianBlur(radius=radius))
    
    out = io.BytesIO()
    blurred_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def sharpen_image(file_bytes: bytes) -> io.BytesIO:
    """Apply sharpen effect to image"""
    img = Image.open(_bytesio(file_bytes))
    sharpened_img = img.filter(ImageFilter.SHARPEN)
    
    out = io.BytesIO()
    sharpened_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def grayscale_image(file_bytes: bytes) -> io.BytesIO:
    """Convert image to grayscale"""
    img = Image.open(_bytesio(file_bytes))
    grayscale_img = img.convert('L')
    
    # Convert back to RGB for consistency
    if grayscale_img.mode != 'RGB':
        grayscale_img = grayscale_img.convert('RGB')
    
    out = io.BytesIO()
    grayscale_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def sepia_image(file_bytes: bytes) -> io.BytesIO:
    """Apply sepia effect to image"""
    img = Image.open(_bytesio(file_bytes))
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Apply sepia effect
    pixels = img.load()
    for i in range(img.width):
        for j in range(img.height):
            r, g, b = pixels[i, j]
            
            # Sepia transformation
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            
            pixels[i, j] = (
                min(255, tr),
                min(255, tg),
                min(255, tb)
            )
    
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def invert_image(file_bytes: bytes) -> io.BytesIO:
    """Invert image colors"""
    img = Image.open(_bytesio(file_bytes))
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Invert colors
    pixels = img.load()
    for i in range(img.width):
        for j in range(img.height):
            r, g, b = pixels[i, j]
            pixels[i, j] = (255 - r, 255 - g, 255 - b)
    
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out
