import io
import os
import zipfile
import base64
from flask import Flask, request, send_file, render_template, jsonify
from werkzeug.utils import secure_filename
from pdf_tools import merge_pdfs, split_pdf_range, rotate_pdf, watermark_pdf_text, add_page_numbers, protect_pdf, unlock_pdf, compress_pdf, pdf_to_images, images_to_pdf, docx_to_pdf, pdf_to_docx, ocr_pdf, compress_pdf_ghostscript, split_pdf_each_page, split_pdf_by_chunks, reorder_pages, remove_pages, extract_images_embedded, add_text_overlay, add_image_overlay, xlsx_to_pdf, pptx_to_pdf, pdf_to_xlsx, pdf_to_pptx, redact_pdf, highlight_pdf, edit_pdf_metadata, get_pdf_metadata, compare_pdfs
import config as app_config

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024
app.config["UPLOAD_EXTENSIONS"] = {".pdf", ".docx", ".xlsx", ".pptx", ".jpg", ".jpeg", ".png"}

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/debug")
def debug():
    return send_file("debug.html")

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

@app.post("/merge")
def merge():
    files = _validate_files(request.files.getlist("files"))
    if not files:
        return {"error": "No valid PDF files provided"}, 400
    buf = merge_pdfs([io.BytesIO(f.read()) for f in files])
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="merged.pdf")

@app.post("/split")
def split():
    f = request.files.get("file")
    start = int(request.form.get("from", "1"))
    end = int(request.form.get("to", "1"))
    if not f:
        return {"error": "No file"}, 400
    buf = split_pdf_range(io.BytesIO(f.read()), start, end)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="split.pdf")

@app.post("/rotate")
def rotate():
    f = request.files.get("file")
    angle = int(request.form.get("angle", "90"))
    pages = request.form.get("pages")
    if not f:
        return {"error": "No file"}, 400
    pages_list = None
    if pages:
        pages_list = [int(x) for x in pages.split(",") if x.strip().isdigit()]
    buf = rotate_pdf(io.BytesIO(f.read()), angle, pages_list)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="rotated.pdf")

@app.post("/watermark")
def watermark():
    f = request.files.get("file")
    text = request.form.get("text", "")
    opacity = float(request.form.get("opacity", "0.2"))
    font_size = int(request.form.get("font_size", "48"))
    if not f or not text:
        return {"error": "File and text required"}, 400
    buf = watermark_pdf_text(io.BytesIO(f.read()), text, opacity, font_size)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="watermarked.pdf")

@app.post("/paginate")
def paginate():
    f = request.files.get("file")
    position = request.form.get("position", "bottom_center")
    font_size = int(request.form.get("font_size", "12"))
    if not f:
        return {"error": "No file"}, 400
    buf = add_page_numbers(io.BytesIO(f.read()), position, font_size)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="numbered.pdf")

@app.post("/protect")
def protect():
    f = request.files.get("file")
    user_password = request.form.get("user_password", "")
    owner_password = request.form.get("owner_password", "")
    if not f or not user_password:
        return {"error": "File and user_password required"}, 400
    buf = protect_pdf(io.BytesIO(f.read()), user_password, owner_password)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="protected.pdf")

@app.post("/unlock")
def unlock():
    f = request.files.get("file")
    password = request.form.get("password", "")
    if not f or not password:
        return {"error": "File and password required"}, 400
    try:
        buf = unlock_pdf(io.BytesIO(f.read()), password)
    except Exception:
        return {"error": "Invalid password or cannot unlock"}, 400
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="unlocked.pdf")

@app.post("/compress")
def compress():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    buf = compress_pdf(io.BytesIO(f.read()))
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="compressed.pdf")

@app.post("/split-pages")
def split_pages():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    items = split_pdf_each_page(io.BytesIO(f.read()))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            z.writestr(name, data)
    out.seek(0)
    return send_file(out, mimetype="application/zip", as_attachment=True, download_name="split_pages.zip")

@app.post("/split-chunks")
def split_chunks():
    f = request.files.get("file")
    size = int(request.form.get("size", "1"))
    if not f or size < 1:
        return {"error": "File and valid size required"}, 400
    items = split_pdf_by_chunks(io.BytesIO(f.read()), size)
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            z.writestr(name, data)
    out.seek(0)
    return send_file(out, mimetype="application/zip", as_attachment=True, download_name="split_chunks.zip")

@app.post("/reorder")
def reorder():
    f = request.files.get("file")
    order = request.form.get("order", "")
    if not f or not order:
        return {"error": "File and order required"}, 400
    order_list = [int(x) for x in order.split(",") if x.strip().isdigit()]
    buf = reorder_pages(io.BytesIO(f.read()), order_list)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="reordered.pdf")

@app.post("/remove-pages")
def remove():
    f = request.files.get("file")
    pages = request.form.get("pages", "")
    if not f or not pages:
        return {"error": "File and pages required"}, 400
    remove_list = [int(x) for x in pages.split(",") if x.strip().isdigit()]
    buf = remove_pages(io.BytesIO(f.read()), remove_list)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="removed.pdf")

@app.post("/extract-images")
def extract_images():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    items = extract_images_embedded(f.read())
    if not items:
        return {"error": "No embedded images found"}, 400
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            z.writestr(name, data)
    out.seek(0)
    return send_file(out, mimetype="application/zip", as_attachment=True, download_name="images.zip")

@app.post("/add-text")
def add_text():
    f = request.files.get("file")
    text = request.form.get("text", "")
    x = float(request.form.get("x", "50"))
    y = float(request.form.get("y", "50"))
    font_size = int(request.form.get("font_size", "12"))
    pages = request.form.get("pages", "")
    if not f or not text:
        return {"error": "File and text required"}, 400
    pages_list = None
    if pages:
        pages_list = [int(x) for x in pages.split(",") if x.strip().isdigit()]
    buf = add_text_overlay(f.read(), text, x, y, font_size, pages_list)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="text.pdf")

@app.post("/add-image")
def add_image():
    f = request.files.get("file")
    img = request.files.get("image")
    x = float(request.form.get("x", "50"))
    y = float(request.form.get("y", "50"))
    width = float(request.form.get("width", "200"))
    height = float(request.form.get("height", "100"))
    pages = request.form.get("pages", "")
    if not f or not img:
        return {"error": "File and image required"}, 400
    pages_list = None
    if pages:
        pages_list = [int(x) for x in pages.split(",") if x.strip().isdigit()]
    buf = add_image_overlay(f.read(), img.read(), x, y, width, height, pages_list)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="image.pdf")
@app.post("/pdf-to-images")
def pdf_to_imgs():
    f = request.files.get("file")
    fmt = request.form.get("format", "png")
    dpi = int(request.form.get("dpi", "144"))
    if not f:
        return {"error": "No file"}, 400
    items = pdf_to_images(io.BytesIO(f.read()), fmt, dpi)
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            z.writestr(name, data)
    out.seek(0)
    return send_file(out, mimetype="application/zip", as_attachment=True, download_name="images.zip")

@app.post("/excel-to-pdf")
def excel_to_pdf():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    name = secure_filename(f.filename or "")
    ext = os.path.splitext(name)[1].lower()
    if ext != ".xlsx":
        return {"error": "Please select an Excel spreadsheet (.xlsx)"}, 400
    try:
        buf = xlsx_to_pdf(f.read())
    except Exception as e:
        return {"error": str(e)}, 400
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="excel.pdf")

@app.post("/powerpoint-to-pdf")
def powerpoint_to_pdf():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    name = secure_filename(f.filename or "")
    ext = os.path.splitext(name)[1].lower()
    if ext != ".pptx":
        return {"error": "Please select a PowerPoint presentation (.pptx)"}, 400
    try:
        buf = pptx_to_pdf(f.read())
    except Exception as e:
        return {"error": str(e)}, 400
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="powerpoint.pdf")

@app.post("/pdf-to-excel")
def pdf_to_excel():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    try:
        buf = pdf_to_xlsx(f.read())
    except Exception as e:
        return {"error": str(e)}, 400
    return send_file(buf, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="converted.xlsx")

@app.post("/pdf-to-powerpoint")
def pdf_to_powerpoint():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    try:
        buf = pdf_to_pptx(f.read())
    except Exception as e:
        return {"error": str(e)}, 400
    return send_file(buf, mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation", as_attachment=True, download_name="converted.pptx")

@app.post("/redact")
def redact():
    f = request.files.get("file")
    rects = request.form.get("rects", "")
    pages = request.form.get("pages", "")
    if not f or not rects:
        return {"error": "File and rects required"}, 400
    pages_list = None
    if pages:
        pages_list = [int(x) for x in pages.split(",") if x.strip().isdigit()]
    try:
        buf = redact_pdf(f.read(), rects, pages_list)
    except Exception as e:
        return {"error": str(e)}, 400
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="redacted.pdf")

@app.post("/highlight")
def highlight():
    f = request.files.get("file")
    rects = request.form.get("rects", "")
    pages = request.form.get("pages", "")
    if not f or not rects:
        return {"error": "File and rects required"}, 400
    pages_list = None
    if pages:
        pages_list = [int(x) for x in pages.split(",") if x.strip().isdigit()]
    try:
        buf = highlight_pdf(f.read(), rects, pages_list)
    except Exception as e:
        return {"error": str(e)}, 400
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="highlighted.pdf")

@app.post("/batch")
def batch():
    files = request.files.getlist("files")
    op = request.form.get("operation", "")
    if not files or not op:
        return {"error": "Files and operation required"}, 400
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            name = secure_filename(f.filename or "file")
            data = f.read()
            try:
                if op == "compress":
                    res = compress_pdf(io.BytesIO(data))
                    z.writestr(os.path.splitext(name)[0] + "_compressed.pdf", res.getvalue())
                elif op == "compress_strong":
                    quality = request.form.get("quality", "screen")
                    res = compress_pdf_ghostscript(data, quality)
                    z.writestr(os.path.splitext(name)[0] + "_strong.pdf", res.getvalue())
                elif op == "ocr":
                    dpi = int(request.form.get("dpi", "200"))
                    res = ocr_pdf(data, dpi)
                    z.writestr(os.path.splitext(name)[0] + "_ocr.pdf", res.getvalue())
                elif op == "office_to_pdf":
                    ext = os.path.splitext(name)[1].lower()
                    if ext == ".docx":
                        res = docx_to_pdf(data)
                    elif ext == ".xlsx":
                        res = xlsx_to_pdf(data)
                    elif ext == ".pptx":
                        res = pptx_to_pdf(data)
                    else:
                        raise RuntimeError("Unsupported office format")
                    z.writestr(os.path.splitext(name)[0] + ".pdf", res.getvalue())
                elif op == "pdf_to_images":
                    fmt = request.form.get("format", "png")
                    dpi = int(request.form.get("dpi", "144"))
                    imgs = pdf_to_images(io.BytesIO(data), fmt, dpi)
                    folder = os.path.splitext(name)[0]
                    for img_name, img_data in imgs:
                        z.writestr(f"{folder}/{img_name}", img_data)
                else:
                    raise RuntimeError("Unsupported operation")
            except Exception as e:
                z.writestr(os.path.splitext(name)[0] + "_error.txt", str(e))
    out.seek(0)
    return send_file(out, mimetype="application/zip", as_attachment=True, download_name="batch_results.zip")

@app.post("/images-to-pdf")
def imgs_to_pdf():
    files = request.files.getlist("files")
    if not files:
        return {"error": "No images"}, 400
    bufs = [io.BytesIO(f.read()) for f in files]
    buf = images_to_pdf(bufs)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="from_images.pdf")

@app.post("/word-to-pdf")
def word_to_pdf():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    name = secure_filename(f.filename or "")
    ext = os.path.splitext(name)[1].lower()
    if ext != ".docx":
        return {"error": "Please select a Word document (.docx)"}, 400
    try:
        buf = docx_to_pdf(f.read())
    except Exception as e:
        return {"error": str(e)}, 400
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="converted.pdf")

@app.post("/pdf-to-word")
def pdf_to_word():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    try:
        buf = pdf_to_docx(f.read())
    except Exception as e:
        return {"error": str(e)}, 400
    return send_file(buf, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document", as_attachment=True, download_name="converted.docx")

@app.post("/ocr")
def ocr():
    f = request.files.get("file")
    dpi = int(request.form.get("dpi", "200"))
    if not f:
        return {"error": "No file"}, 400
    try:
        buf = ocr_pdf(f.read(), dpi)
    except Exception as e:
        return {"error": str(e)}, 400
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="ocr.pdf")

@app.post("/compress-strong")
def compress_strong():
    f = request.files.get("file")
    quality = request.form.get("quality", "screen")
    if not f:
        return {"error": "No file"}, 400
    buf = compress_pdf_ghostscript(f.read(), quality)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="compressed_strong.pdf")

@app.get("/settings")
def get_settings():
    cfg = app_config.load()
    return jsonify({
        "config": cfg
    })

@app.post("/settings")
def set_settings():
    data = {
        "tesseract_path": request.form.get("tesseract_path", ""),
        "libreoffice_path": request.form.get("libreoffice_path", ""),
        "ghostscript_path": request.form.get("ghostscript_path", "")
    }
    cfg = app_config.save(data)
    return jsonify({"config": cfg})

@app.post("/edit-metadata")
def edit_metadata():
    f = request.files.get("file")
    title = request.form.get("title", "")
    author = request.form.get("author", "")
    subject = request.form.get("subject", "")
    keywords = request.form.get("keywords", "")
    if not f:
        return {"error": "No file"}, 400
    buf = edit_pdf_metadata(f.read(), title, author, subject, keywords)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="metadata_edited.pdf")

@app.get("/get-metadata")
def get_metadata():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    try:
        metadata = get_pdf_metadata(f.read())
        return jsonify({"metadata": metadata})
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/compare")
def compare():
    file1 = request.files.get("file1")
    file2 = request.files.get("file2")
    if not file1 or not file2:
        return {"error": "Both files required"}, 400
    buf = compare_pdfs(file1.read(), file2.read())
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="comparison.pdf")

@app.post("/pdf-preview")
def pdf_preview():
    f = request.files.get("file")
    if not f:
        return {"error": "No file"}, 400
    try:
        import fitz
        doc = fitz.open(stream=f.read(), filetype="pdf")
        metadata = doc.metadata
        page_count = len(doc)
        
        # Get first page as thumbnail
        first_page = doc.load_page(0)
        pix = first_page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))
        img_data = pix.tobytes("png")
        
        return jsonify({
            "page_count": page_count,
            "metadata": metadata,
            "thumbnail": "data:image/png;base64," + base64.b64encode(img_data).decode()
        })
    except Exception as e:
        return {"error": str(e)}, 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    print(f"Server running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port)
