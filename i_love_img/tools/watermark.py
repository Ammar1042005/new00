import io
from PIL import Image, ImageDraw, ImageFont

def _bytesio(data: bytes) -> io.BytesIO:
    buf = io.BytesIO()
    buf.write(data)
    buf.seek(0)
    return buf

def add_watermark(file_bytes: bytes, text: str, position: str = "bottom-right") -> io.BytesIO:
    """Add text watermark to image"""
    img = Image.open(_bytesio(file_bytes))
    
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
