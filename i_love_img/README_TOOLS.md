# I Love Img - Modular Tool Structure

## Overview
The application has been restructured into separate modules for better organization and maintainability.

## Tool Modules

### 1. `tools/basic_tools.py`
Contains fundamental image operations:
- `compress_image()` - Compress images with quality control
- `resize_image()` - Resize images with aspect ratio options
- `crop_image()` - Crop images to specified area
- `rotate_image()` - Rotate images by specified angle
- `convert_image()` - Convert between image formats
- `flip_image()` - Flip images horizontally/vertically
- `upscale_image()` - Upscale images with scale factor

### 2. `tools/adjustments.py`
Contains image enhancement functions:
- `adjust_brightness()` - Adjust image brightness
- `adjust_contrast()` - Adjust image contrast
- `adjust_saturation()` - Adjust image saturation

### 3. `tools/effects.py`
Contains artistic effects:
- `blur_image()` - Apply Gaussian blur
- `sharpen_image()` - Apply sharpening filter
- `grayscale_image()` - Convert to grayscale
- `sepia_image()` - Apply sepia tone effect
- `invert_image()` - Invert image colors

### 4. `tools/background_removal.py`
Contains background removal functions:
- `remove_background_automatic()` - Automatic background detection
- `remove_background_color()` - Remove specific color within tolerance

### 5. `tools/watermark.py`
Contains watermark functionality:
- `add_watermark()` - Add text watermarks at various positions

### 6. `tools/batch_processing.py`
Contains batch processing capabilities:
- `batch_process_images()` - Process multiple images with same operation

### 7. `tools/__init__.py`
Module initialization file that imports all tool modules.

## API Endpoints

### Basic Tools
- `POST /compress` - Compress image
- `POST /resize` - Resize image
- `POST /crop` - Crop image
- `POST /rotate` - Rotate image
- `POST /convert` - Convert image format
- `POST /flip` - Flip image (GUI tool)
- `POST /upscale` - Upscale image (GUI tool)

### Adjustments
- `POST /enhance-brightness` - Adjust brightness
- `POST /enhance-contrast` - Adjust contrast
- `POST /enhance-saturation` - Adjust saturation

### Effects
- `POST /blur` - Apply blur effect
- `POST /sharpen` - Apply sharpen effect
- `POST /grayscale` - Convert to grayscale
- `POST /sepia` - Apply sepia effect
- `POST /invert` - Invert colors

### Advanced Tools
- `POST /add-watermark` - Add watermark
- `POST /remove-background` - Remove background
- `POST /batch-process` - Batch process images

### Utilities
- `POST /image-preview` - Generate image preview and info

## Benefits of Modular Structure

1. **Better Organization**: Related functions grouped together
2. **Easier Maintenance**: Changes to specific tools isolated
3. **Reusability**: Tools can be imported and used independently
4. **Testing**: Each module can be tested separately
5. **Scalability**: Easy to add new tools without affecting existing code

## Usage Example

```python
from tools import basic_tools, adjustments, effects

# Load image
with open('image.jpg', 'rb') as f:
    image_data = f.read()

# Apply operations
compressed = basic_tools.compress_image(image_data, quality=85)
brightened = adjustments.adjust_brightness(image_data, factor=1.2)
blurred = effects.blur_image(image_data, radius=2.0)
```

## Dependencies

- Pillow (PIL) for image processing
- NumPy for advanced image operations
- Flask for web interface
- All dependencies listed in `requirements.txt`
