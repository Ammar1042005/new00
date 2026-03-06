import io
import os
import base64
from flask import Flask, request, send_file, render_template, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from tools import basic_tools, adjustments, effects, background_removal, watermark, batch_processing
import config as app_config

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024
app.config["UPLOAD_EXTENSIONS"] = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/editor")
def editor():
    return render_template("editor.html")

@app.get("/settings")
def get_settings():
    cfg = app_config.load()
    return jsonify({"config": cfg})

@app.post("/settings")
def set_settings():
    data = {
        "default_quality": request.form.get("default_quality", "90"),
        "default_format": request.form.get("default_format", "JPEG"),
    }
    cfg = app_config.save(data)
    return jsonify({"config": cfg})

def _validate_files(files):
    valid = []
    for f in files:
        if not f:
            continue
        name = secure_filename(f.filename or "")
        ext = os.path.splitext(name)[1].lower()
        if ext not in app.config["UPLOAD_EXTENSIONS"]:
            continue
        valid.append(f)
    return valid

# Image Conversion Tools
@app.post("/compress")
def compress():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file provided"}), 400
    
    quality = int(request.form.get("quality", 90))
    
    try:
        result = basic_tools.compress_image(f.read(), quality)
        return send_file(
            io.BytesIO(result.getvalue()),
            mimetype="image/jpeg",
            as_attachment=True,
            download_name="compressed.jpg"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/resize")
def resize():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    width = int(request.form.get("width", 800))
    height = int(request.form.get("height", 600))
    try:
        buf = basic_tools.resize_image(f.read(), width, height)
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="resized.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/crop")
def crop():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    x = int(request.form.get("x", 0))
    y = int(request.form.get("y", 0))
    width = int(request.form.get("width", 100))
    height = int(request.form.get("height", 100))
    try:
        buf = basic_tools.crop_image(f.read(), x, y, width, height)
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="cropped.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/rotate")
def rotate():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    angle = int(request.form.get("angle", 90))
    try:
        buf = basic_tools.rotate_image(f.read(), angle)
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="rotated.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/convert")
def convert():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    format = request.form.get("format", "PNG").upper()
    try:
        buf = basic_tools.convert_image(f.read(), format)
        mimetype = f"image/{format.lower()}"
        return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=f"converted.{format.lower()}")
    except Exception as e:
        return {"error": str(e)}, 400

# Image Enhancement Tools
@app.post("/enhance-brightness")
def enhance_brightness():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    percentage = float(request.form.get("factor", 100))
    # Convert percentage to factor where 100% = 1.0 (normal)
    factor = percentage / 100
    try:
        buf = adjustments.adjust_brightness(f.read(), factor)
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="brightness.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/enhance-contrast")
def enhance_contrast():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    percentage = float(request.form.get("factor", 100))
    # Convert percentage to factor where 100% = 1.0 (normal)
    factor = percentage / 100
    try:
        buf = adjustments.adjust_contrast(f.read(), factor)
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="contrast.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/enhance-saturation")
def enhance_saturation():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    percentage = float(request.form.get("factor", 100))
    # Convert percentage to factor where 100% = 1.0 (normal)
    factor = percentage / 100
    try:
        buf = adjustments.adjust_saturation(f.read(), factor)
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="saturation.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/blur")
def blur():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    radius = float(request.form.get("radius", 2.0))
    try:
        buf = effects.blur_image(f.read(), radius)
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="blurred.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/sharpen")
def sharpen():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    try:
        buf = effects.sharpen_image(f.read())
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="sharpened.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

# Image Effects
@app.post("/grayscale")
def grayscale():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    try:
        buf = effects.grayscale_image(f.read())
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="grayscale.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/sepia")
def sepia():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    try:
        buf = effects.sepia_image(f.read())
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="sepia.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/invert")
def invert():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    try:
        buf = effects.invert_image(f.read())
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="inverted.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

# Watermark
@app.post("/add-watermark")
def add_watermark():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    text = request.form.get("text", "Watermark")
    position = request.form.get("position", "bottom-right")
    try:
        buf = watermark.add_watermark(f.read(), text, position)
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="watermarked.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

# Batch Processing
@app.post("/batch-process")
def batch_process():
    files = _validate_files(request.files.getlist("files"))
    if not files:
        return {"error": "No valid image files provided"}, 400
    
    operation = request.form.get("operation", "compress")
    params = {}
    
    if operation == "compress":
        params["quality"] = int(request.form.get("quality", 90))
    elif operation == "resize":
        params["width"] = int(request.form.get("width", 800))
        params["height"] = int(request.form.get("height", 600))
    elif operation == "convert":
        params["format"] = request.form.get("format", "PNG").upper()
    
    try:
        result = batch_processing.batch_process_images(files, operation, **params)
        return send_file(result, mimetype="application/zip", as_attachment=True, download_name="batch_processed.zip")
    
    except Exception as e:
        return {"error": str(e)}, 400

# GUI-Specific Tools
@app.post("/flip")
def flip():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    horizontal = request.form.get("horizontal", "true").lower() == "true"
    try:
        buf = basic_tools.flip_image(f.read(), horizontal)
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="flipped.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/upscale")
def upscale():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    scale_factor = int(request.form.get("scale_factor", 2))
    try:
        buf = basic_tools.upscale_image(f.read(), scale_factor)
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="upscaled.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/remove-background")
def remove_background():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    
    mode = request.form.get("mode", "automatic")
    
    try:
        if mode == "color":
            hex_color = request.form.get("color", "#ffffff")
            tolerance = int(request.form.get("tolerance", 30))
            buf = background_removal.remove_background_color(f.read(), hex_color, tolerance)
        else:
            strength = request.form.get("strength", "moderate")
            preserve_edges = request.form.get("preserve_edges", "true").lower() == "true"
            buf = background_removal.remove_background_automatic(f.read(), strength, preserve_edges)
        
        return send_file(buf, mimetype="image/jpeg", as_attachment=True, download_name="background_removed.jpg")
    except Exception as e:
        return {"error": str(e)}, 400

# Image Preview
@app.post("/image-preview")
def image_preview():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    try:
        img = Image.open(io.BytesIO(f.read()))
        
        # Create thumbnail
        img.thumbnail((200, 200))
        thumb_buffer = io.BytesIO()
        img.save(thumb_buffer, format="JPEG", quality=85)
        thumb_data = base64.b64encode(thumb_buffer.getvalue()).decode()
        
        # Get image info
        info = {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "size": len(f.read()) if hasattr(f, 'seek') else 0,
            "thumbnail": f"data:image/jpeg;base64,{thumb_data}"
        }
        
        return jsonify(info)
    except Exception as e:
        return {"error": str(e)}, 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    print(f"Server running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port)
