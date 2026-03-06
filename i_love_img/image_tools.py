import io
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import os

def _bytesio(data: bytes) -> io.BytesIO:
    buf = io.BytesIO()
    buf.write(data)
    buf.seek(0)
    return buf

# Basic Image Operations
def compress_image(file_bytes: bytes, quality: int = 90) -> io.BytesIO:
    img = Image.open(io.BytesIO(file_bytes))
    
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
    img = Image.open(io.BytesIO(file_bytes))
    
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
    img = Image.open(io.BytesIO(file_bytes))
    
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
    img = Image.open(io.BytesIO(file_bytes))
    
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
    img = Image.open(io.BytesIO(file_bytes))
    
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

# Image Enhancement
def enhance_brightness(file_bytes: bytes, factor: float = 1.2) -> io.BytesIO:
    img = Image.open(io.BytesIO(file_bytes))
    enhancer = ImageEnhance.Brightness(img)
    enhanced_img = enhancer.enhance(factor)
    
    out = io.BytesIO()
    enhanced_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def enhance_contrast(file_bytes: bytes, factor: float = 1.2) -> io.BytesIO:
    img = Image.open(io.BytesIO(file_bytes))
    enhancer = ImageEnhance.Contrast(img)
    enhanced_img = enhancer.enhance(factor)
    
    out = io.BytesIO()
    enhanced_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def enhance_saturation(file_bytes: bytes, factor: float = 1.2) -> io.BytesIO:
    img = Image.open(io.BytesIO(file_bytes))
    enhancer = ImageEnhance.Color(img)
    enhanced_img = enhancer.enhance(factor)
    
    out = io.BytesIO()
    enhanced_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

# Image Filters
def blur_image(file_bytes: bytes, radius: float = 2.0) -> io.BytesIO:
    img = Image.open(io.BytesIO(file_bytes))
    blurred_img = img.filter(ImageFilter.GaussianBlur(radius=radius))
    
    out = io.BytesIO()
    blurred_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def sharpen_image(file_bytes: bytes) -> io.BytesIO:
    img = Image.open(io.BytesIO(file_bytes))
    sharpened_img = img.filter(ImageFilter.SHARPEN)
    
    out = io.BytesIO()
    sharpened_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

# Image Effects
def grayscale_image(file_bytes: bytes) -> io.BytesIO:
    img = Image.open(io.BytesIO(file_bytes))
    grayscale_img = img.convert('L')
    
    # Convert back to RGB for consistency
    if grayscale_img.mode != 'RGB':
        grayscale_img = grayscale_img.convert('RGB')
    
    out = io.BytesIO()
    grayscale_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def sepia_image(file_bytes: bytes) -> io.BytesIO:
    img = Image.open(io.BytesIO(file_bytes))
    
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
    img = Image.open(io.BytesIO(file_bytes))
    
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

# Watermark
def add_watermark(file_bytes: bytes, text: str, position: str = "bottom-right") -> io.BytesIO:
    img = Image.open(io.BytesIO(file_bytes))
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default if not available
    try:
        font_size = max(20, min(img.width, img.height) // 20)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position
    margin = 20
    if position == "top-left":
        x, y = margin, margin
    elif position == "top-right":
        x, y = img.width - text_width - margin, margin
    elif position == "bottom-left":
        x, y = margin, img.height - text_height - margin
    elif position == "bottom-right":
        x, y = img.width - text_width - margin, img.height - text_height - margin
    elif position == "center":
        x, y = (img.width - text_width) // 2, (img.height - text_height) // 2
    else:
        x, y = img.width - text_width - margin, img.height - text_height - margin
    
    # Draw semi-transparent background
    padding = 5
    draw.rectangle(
        [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
        fill=(255, 255, 255, 200)
    )
    
    # Draw text
    draw.text((x, y), text, fill=(0, 0, 0), font=font)
    
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

# Image Metadata
def get_image_info(file_bytes: bytes) -> dict:
    img = Image.open(io.BytesIO(file_bytes))
    
    return {
        "width": img.width,
        "height": img.height,
        "format": img.format,
        "mode": img.mode,
        "size": len(file_bytes)
    }
