# I Love Img - Complete Image Processing Suite

A comprehensive web-based image processing application with both classic tools and advanced GUI editor, built with Flask and modern web technologies.

## 🚀 Features

### **Classic Image Tools**
- **Compression** - Reduce file size with quality control
- **Resize** - Change dimensions with aspect ratio options
- **Crop** - Selective area removal
- **Rotate** - Angle-based rotation
- **Convert** - Format conversion (PNG, JPG, WebP, etc.)
- **Flip** - Horizontal/vertical flipping
- **Upscale** - AI-powered image upscaling

### **Advanced GUI Editor**
- **Canvas-based editing** with real-time preview
- **Adjustments** - Brightness, Contrast, Saturation
- **Effects** - Blur, Sharpen, Grayscale, Sepia, Invert
- **Background Removal** - Automatic detection and color-based removal
- **Watermark** - Text watermarks with positioning
- **Batch Processing** - Multiple image operations
- **Undo/Redo** - Complete history management
- **Zoom & Pan** - Advanced canvas navigation

### **Background Removal Modes**
- **Automatic Detection** - Conservative/Moderate/Aggressive strength
- **Color Brush Selection** - Pick specific colors to remove
- **Brush Painting** - Click and drag to paint/remove areas
- **Edge Preservation** - Maintain important details

## 🛠️ Technical Stack

### **Backend**
- **Flask** - Web framework
- **Pillow (PIL)** - Image processing
- **Modular Architecture** - Separate tool modules
- **REST API** - Clean endpoint structure

### **Frontend**
- **HTML5 Canvas** - Real-time image editing
- **Modern JavaScript** - ES6+ features
- **Responsive CSS** - Mobile-friendly design
- **Drag & Drop** - Intuitive file upload

### **Architecture**
```
project/
├── app.py                 # Main Flask application
├── tools/                 # Modular tool structure
│   ├── __init__.py
│   ├── basic_tools.py     # Core operations
│   ├── adjustments.py      # Brightness/Contrast/Saturation
│   ├── effects.py         # Artistic effects
│   ├── background_removal.py  # Background removal
│   ├── watermark.py       # Watermarking
│   └── batch_processing.py # Batch operations
├── static/
│   ├── js/
│   │   ├── canvas-editor.js  # GUI editor logic
│   │   └── main.js         # Classic tools
│   └── css/
│       └── style.css        # Modern styling
└── templates/
    ├── index.html          # Classic tools interface
    └── editor.html         # Advanced GUI editor
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- pip (Python package manager)

### **Installation**
```bash
# Clone the repository
git clone <repository-url>
cd new00

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### **Access Points**
- **Classic Tools**: http://localhost:5001
- **GUI Editor**: http://localhost:5001/editor
- **API Endpoints**: http://localhost:5001/api/

## 📋 API Endpoints

### **Basic Tools**
- `POST /compress` - Compress image
- `POST /resize` - Resize image
- `POST /crop` - Crop image
- `POST /rotate` - Rotate image
- `POST /convert` - Convert format
- `POST /flip` - Flip image
- `POST /upscale` - Upscale image

### **Adjustments**
- `POST /enhance-brightness` - Adjust brightness
- `POST /enhance-contrast` - Adjust contrast
- `POST /enhance-saturation` - Adjust saturation

### **Effects**
- `POST /blur` - Apply blur
- `POST /sharpen` - Apply sharpen
- `POST /grayscale` - Convert to grayscale
- `POST /sepia` - Apply sepia effect
- `POST /invert` - Invert colors

### **Advanced Tools**
- `POST /add-watermark` - Add watermark
- `POST /remove-background` - Remove background
- `POST /batch-process` - Process multiple images

### **Utilities**
- `POST /image-preview` - Generate preview

## 🎨 Usage Examples

### **Classic Tool Usage**
```javascript
// Upload image and apply compression
fetch('/compress', {
    method: 'POST',
    body: formData
}).then(response => response.blob())
  .then(blob => downloadImage(blob, 'compressed.jpg'));
```

### **GUI Editor Usage**
```javascript
// Initialize canvas editor
const editor = new CanvasEditor('image-canvas');

// Apply adjustments
editor.adjustBrightness(1.5);  // 150% brightness
editor.adjustContrast(1.2);     // 120% contrast
editor.adjustSaturation(0.8);    // 80% saturation

// Apply effects
editor.grayscale();
editor.sepia();
editor.blur(2.0);

// Background removal
editor.removeBackground('moderate', true);  // Automatic
editor.removeColorBrush('#ffffff', 30);      // Color-based
```

## 🔧 Configuration

### **Environment Variables**
```bash
PORT=5001                    # Server port
MAX_CONTENT_LENGTH=209715200 # Max upload size (200MB)
```

### **Settings**
- **Default Quality**: 90%
- **Default Format**: JPEG
- **History Limit**: 20 states
- **Supported Formats**: JPG, PNG, GIF, BMP, WebP, TIFF

## 🎯 Key Features

### **Non-Destructive Editing**
- All adjustments work from original image state
- 100% = Normal baseline for all adjustments
- Undo/Redo with complete history
- Reset to original anytime

### **Advanced Background Removal**
- **Automatic Detection**: Smart background identification
- **Color Selection**: Pick specific colors to remove
- **Brush Tool**: Paint areas to remove
- **Edge Preservation**: Maintain important details
- **Tolerance Control**: Fine-tune color matching

### **Professional GUI Editor**
- **Real-time Preview**: Instant visual feedback
- **Zoom & Pan**: Navigate large images
- **Cumulative Effects**: Stack multiple adjustments
- **Batch Operations**: Process multiple images
- **Export Options**: Multiple format support

## 🧪 Development

### **Modular Structure**
Each tool category is in its own module:
- `tools/basic_tools.py` - Core operations
- `tools/adjustments.py` - Image enhancements
- `tools/effects.py` - Artistic effects
- `tools/background_removal.py` - Background removal
- `tools/watermark.py` - Watermarking
- `tools/batch_processing.py` - Batch operations

### **Adding New Tools**
1. Create function in appropriate module
2. Add endpoint in `app.py`
3. Update frontend if needed
4. Test thoroughly

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Add tests if applicable
5. Submit pull request

## 📞 Support

For issues, questions, or contributions:
- Create an issue in the repository
- Check existing documentation
- Review code examples

---

**Built with ❤️ using Flask, Pillow, and modern web technologies**
