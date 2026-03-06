import io
from PIL import Image, ImageEnhance

def _bytesio(data: bytes) -> io.BytesIO:
    buf = io.BytesIO()
    buf.write(data)
    buf.seek(0)
    return buf

def adjust_brightness(file_bytes: bytes, factor: float = 1.2) -> io.BytesIO:
    """Adjust image brightness - factor where 1.0 = normal (100%)"""
    img = Image.open(_bytesio(file_bytes))
    enhancer = ImageEnhance.Brightness(img)
    enhanced_img = enhancer.enhance(factor)
    
    out = io.BytesIO()
    enhanced_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def adjust_contrast(file_bytes: bytes, factor: float = 1.2) -> io.BytesIO:
    """Adjust image contrast - factor where 1.0 = normal (100%)"""
    img = Image.open(_bytesio(file_bytes))
    enhancer = ImageEnhance.Contrast(img)
    enhanced_img = enhancer.enhance(factor)
    
    out = io.BytesIO()
    enhanced_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def adjust_saturation(file_bytes: bytes, factor: float = 1.2) -> io.BytesIO:
    """Adjust image saturation - factor where 1.0 = normal (100%)"""
    img = Image.open(_bytesio(file_bytes))
    enhancer = ImageEnhance.Color(img)
    enhanced_img = enhancer.enhance(factor)
    
    out = io.BytesIO()
    enhanced_img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out
