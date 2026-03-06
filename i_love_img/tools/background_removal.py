import io
from PIL import Image, ImageFilter, ImageEnhance

def _bytesio(data: bytes) -> io.BytesIO:
    buf = io.BytesIO()
    buf.write(data)
    buf.seek(0)
    return buf

def remove_background_automatic(file_bytes: bytes, strength: str = 'moderate', preserve_edges: bool = True) -> io.BytesIO:
    """Remove background automatically with specified strength"""
    img = Image.open(_bytesio(file_bytes))
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Set thresholds based on strength
    if strength == 'conservative':
        threshold = 220
        variance_threshold = 20
    elif strength == 'aggressive':
        threshold = 180
        variance_threshold = 40
    else:  # moderate
        threshold = 200
        variance_threshold = 30
    
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            
            # Calculate brightness and color variance
            brightness = (r + g + b) / 3
            color_variance = abs(r - g) + abs(g - b) + abs(r - b)
            
            # Check if pixel should be removed
            should_remove = brightness > threshold and color_variance < variance_threshold
            
            # Edge preservation logic
            if preserve_edges and should_remove:
                is_edge = False
                # Check neighboring pixels
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < img.width and 0 <= ny < img.height:
                            nr, ng, nb = pixels[nx, ny]
                            neighbor_brightness = (nr + ng + nb) / 3
                            if abs(brightness - neighbor_brightness) > 50:
                                is_edge = True
                                break
                    if is_edge:
                        break
                
                should_remove = not is_edge
            
            # Apply background removal
            if should_remove:
                pixels[x, y] = (255, 255, 255)  # Pure white
    
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out

def remove_background_color(file_bytes: bytes, hex_color: str, tolerance: int = 30) -> io.BytesIO:
    """Remove specific color within tolerance range"""
    img = Image.open(_bytesio(file_bytes))
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convert hex color to RGB
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            pixel_r, pixel_g, pixel_b = pixels[x, y]
            
            # Calculate color distance
            color_distance = ((pixel_r - r)**2 + (pixel_g - g)**2 + (pixel_b - b)**2)**0.5
            
            # Remove pixels within tolerance range
            if color_distance <= tolerance * 2.55:  # Convert tolerance (0-100) to RGB scale (0-255)
                pixels[x, y] = (255, 255, 255)  # Pure white
    
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=95)
    out.seek(0)
    return out
