class ImageTools {
    constructor() {
        this.initializeEventListeners();
        this.loadSettings();
    }

    initializeEventListeners() {
        // File input listeners for preview
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', (e) => this.validateFileInput(e));
        });

        // Range input listeners for value display
        document.querySelectorAll('input[type="range"]').forEach(input => {
            input.addEventListener('input', (e) => this.updateRangeValue(e));
        });

        // Button listeners
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleButtonClick(e));
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    validateFileInput(e) {
        const input = e.target;
        const files = Array.from(input.files);
        const maxSize = 200 * 1024 * 1024; // 200MB

        for (const file of files) {
            if (file.size > maxSize) {
                this.showError(input.parentElement, `File "${file.name}" is too large (max 200MB)`);
                input.value = '';
                return;
            }

            // Check if it's an image file
            if (!file.type.startsWith('image/')) {
                this.showError(input.parentElement, `File "${file.name}" is not a supported image type`);
                input.value = '';
                return;
            }
        }

        // Show file preview
        this.showFilePreview(input, files);
    }

    showFilePreview(input, files) {
        const card = input.closest('.tool-card');
        let previewContainer = card.querySelector('.file-preview');
        
        // Remove existing preview if any
        if (previewContainer) {
            previewContainer.remove();
        }

        if (files.length === 0) return;

        // Create preview container
        previewContainer = document.createElement('div');
        previewContainer.className = 'file-preview';
        previewContainer.innerHTML = '<h4>🖼️ Image Preview</h4>';
        
        const fileList = document.createElement('div');
        fileList.className = 'file-list';

        files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const fileInfo = document.createElement('div');
            fileInfo.className = 'file-info';
            
            // File icon based on type
            const icon = this.getFileIcon(file.name);
            fileInfo.innerHTML = `
                <span class="file-icon">${icon}</span>
                <div class="file-details">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${this.formatFileSize(file.size)}</div>
                </div>
            `;
            
            fileItem.appendChild(fileInfo);
            
            // Add image preview
            this.createImagePreview(file, fileItem);
            
            fileList.appendChild(fileItem);
        });

        previewContainer.appendChild(fileList);
        
        // Insert preview after the input
        input.parentElement.insertBefore(previewContainer, input.parentElement.querySelector('.output-area'));
    }

    getFileIcon(fileName) {
        const ext = fileName.toLowerCase().split('.').pop();
        const icons = {
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️',
            'gif': '🖼️',
            'bmp': '🖼️',
            'webp': '🖼️',
            'tiff': '🖼️',
            'default': '📎'
        };
        return icons[ext] || icons['default'];
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    createImagePreview(file, fileItem) {
        const preview = document.createElement('div');
        preview.className = 'preview-content';
        
        // Show loading state
        preview.innerHTML = `
            <div class="image-preview">
                <div class="image-loading">🖼️ Loading preview...</div>
            </div>
        `;
        
        // Create image preview
        const img = document.createElement('img');
        img.className = 'preview-image';
        img.style.maxWidth = '200px';
        img.style.maxHeight = '150px';
        img.style.objectFit = 'contain';
        
        const reader = new FileReader();
        reader.onload = (e) => {
            img.src = e.target.result;
            preview.innerHTML = '';
            preview.appendChild(img);
        };
        reader.readAsDataURL(file);
        
        fileItem.appendChild(preview);
    }

    updateRangeValue(e) {
        const input = e.target;
        const valueDisplay = input.parentElement.querySelector('span');
        if (valueDisplay) {
            if (input.id.includes('quality')) {
                valueDisplay.textContent = input.value + '%';
            } else {
                valueDisplay.textContent = input.value;
            }
        }
    }

    async handleButtonClick(e) {
        const btn = e.target;
        const card = btn.closest('.tool-card');
        
        if (btn.disabled) return;

        // Show loading state
        this.setButtonLoading(btn, true);
        this.clearMessages(card);

        try {
            await this.executeToolAction(btn, card);
        } catch (error) {
            this.showError(card.querySelector('.output-area'), error.message || 'An error occurred');
        } finally {
            this.setButtonLoading(btn, false);
        }
    }

    async executeToolAction(btn, card) {
        const toolName = btn.getAttribute('onclick')?.match(/(\w+)\(\))/)?.[1];
        if (!toolName) return;

        switch (toolName) {
            case 'compress_image':
                await this.compressImage(card);
                break;
            case 'resize_image':
                await this.resizeImage(card);
                break;
            case 'crop_image':
                await this.cropImage(card);
                break;
            case 'rotate_image':
                await this.rotateImage(card);
                break;
            case 'convert_image':
                await this.convertImage(card);
                break;
            case 'adjust_brightness':
                await this.adjustBrightness(card);
                break;
            case 'adjust_contrast':
                await this.adjustContrast(card);
                break;
            case 'adjust_saturation':
                await this.adjustSaturation(card);
                break;
            case 'blur_image':
                await this.blurImage(card);
                break;
            case 'sharpen_image':
                await this.sharpenImage(card);
                break;
            case 'grayscale_image':
                await this.grayscaleImage(card);
                break;
            case 'sepia_image':
                await this.sepiaImage(card);
                break;
            case 'invert_image':
                await this.invertImage(card);
                break;
            case 'add_watermark':
                await this.addWatermark(card);
                break;
            case 'batch_process':
                await this.batchProcess(card);
                break;
            case 'save_settings':
                await this.saveSettings(card);
                break;
        }
    }

    async compressImage(card) {
        const fileInput = card.querySelector('#compress-file');
        const quality = card.querySelector('#compress-quality').value;
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('quality', quality);

        const response = await fetch('/compress', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'compressed.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Image compressed successfully!');
    }

    async resizeImage(card) {
        const fileInput = card.querySelector('#resize-file');
        const width = card.querySelector('#resize-width').value;
        const height = card.querySelector('#resize-height').value;
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('width', width);
        formData.append('height', height);

        const response = await fetch('/resize', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'resized.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Image resized successfully!');
    }

    async cropImage(card) {
        const fileInput = card.querySelector('#crop-file');
        const x = card.querySelector('#crop-x').value;
        const y = card.querySelector('#crop-y').value;
        const width = card.querySelector('#crop-width').value;
        const height = card.querySelector('#crop-height').value;
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('x', x);
        formData.append('y', y);
        formData.append('width', width);
        formData.append('height', height);

        const response = await fetch('/crop', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'cropped.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Image cropped successfully!');
    }

    async rotateImage(card) {
        const fileInput = card.querySelector('#rotate-file');
        const angle = card.querySelector('#rotate-angle').value;
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('angle', angle);

        const response = await fetch('/rotate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'rotated.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Image rotated successfully!');
    }

    async convertImage(card) {
        const fileInput = card.querySelector('#convert-file');
        const format = card.querySelector('#convert-format').value;
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('format', format);

        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, `converted.${format.toLowerCase()}`);
        this.showSuccess(card.querySelector('.output-area'), `Image converted to ${format} successfully!`);
    }

    async adjustBrightness(card) {
        const fileInput = card.querySelector('#brightness-file');
        const factor = card.querySelector('#brightness-factor').value;
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('factor', factor);

        const response = await fetch('/enhance-brightness', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'brightness.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Brightness adjusted successfully!');
    }

    async adjustContrast(card) {
        const fileInput = card.querySelector('#contrast-file');
        const factor = card.querySelector('#contrast-factor').value;
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('factor', factor);

        const response = await fetch('/enhance-contrast', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'contrast.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Contrast adjusted successfully!');
    }

    async adjustSaturation(card) {
        const fileInput = card.querySelector('#saturation-file');
        const factor = card.querySelector('#saturation-factor').value;
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('factor', factor);

        const response = await fetch('/enhance-saturation', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'saturation.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Saturation adjusted successfully!');
    }

    async blurImage(card) {
        const fileInput = card.querySelector('#blur-file');
        const radius = card.querySelector('#blur-radius').value;
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('radius', radius);

        const response = await fetch('/blur', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'blurred.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Image blurred successfully!');
    }

    async sharpenImage(card) {
        const fileInput = card.querySelector('#sharpen-file');
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch('/sharpen', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'sharpened.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Image sharpened successfully!');
    }

    async grayscaleImage(card) {
        const fileInput = card.querySelector('#grayscale-file');
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch('/grayscale', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'grayscale.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Image converted to grayscale!');
    }

    async sepiaImage(card) {
        const fileInput = card.querySelector('#sepia-file');
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch('/sepia', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'sepia.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Sepia effect applied!');
    }

    async invertImage(card) {
        const fileInput = card.querySelector('#invert-file');
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch('/invert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'inverted.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Colors inverted!');
    }

    async addWatermark(card) {
        const fileInput = card.querySelector('#watermark-file');
        const text = card.querySelector('#watermark-text').value;
        const position = card.querySelector('#watermark-position').value;
        
        if (!fileInput.files[0]) {
            throw new Error('Please select an image file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('text', text);
        formData.append('position', position);

        const response = await fetch('/add-watermark', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'watermarked.jpg');
        this.showSuccess(card.querySelector('.output-area'), 'Watermark added!');
    }

    async batchProcess(card) {
        const fileInput = card.querySelector('#batch-files');
        const operation = card.querySelector('#batch-op').value;
        const quality = card.querySelector('#batch-quality').value;
        const format = card.querySelector('#batch-format').value;
        
        if (!fileInput.files[0]) {
            throw new Error('Please select image files');
        }

        const formData = new FormData();
        for (const file of fileInput.files) {
            formData.append('files', file);
        }
        formData.append('operation', operation);
        formData.append('quality', quality);
        formData.append('format', format);

        const response = await fetch('/batch-process', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const blob = await response.blob();
        this.downloadFile(blob, 'batch_processed.zip');
        this.showSuccess(card.querySelector('.output-area'), 'Batch processing completed!');
    }

    async saveSettings(card) {
        const defaultQuality = card.querySelector('#default-quality').value;
        const defaultFormat = card.querySelector('#default-format').value;

        const formData = new FormData();
        formData.append('default_quality', defaultQuality);
        formData.append('default_format', defaultFormat);

        const response = await fetch('/settings', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const data = await response.json();
        this.showSuccess(card.querySelector('#settings-out'), 'Settings saved successfully!');
    }

    async loadSettings() {
        try {
            const response = await fetch('/settings');
            const data = await response.json();
            
            const config = data.config;
            document.getElementById('default-quality').value = config.default_quality || 90;
            document.getElementById('default-format').value = config.default_format || 'JPEG';
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }

    downloadFile(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    setButtonLoading(btn, loading) {
        if (loading) {
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> Processing...';
        } else {
            btn.disabled = false;
            btn.innerHTML = btn.getAttribute('data-original-text') || btn.textContent;
        }
    }

    showSuccess(element, message) {
        element.className = 'output-area success-message';
        element.textContent = message;
    }

    showError(element, message) {
        element.className = 'output-area error-message';
        element.textContent = message;
    }

    showLoading(element, message = 'Processing...') {
        element.className = 'output-area loading-message';
        element.innerHTML = `<span class="loading"></span> ${message}`;
    }

    clearMessages(card) {
        card.querySelectorAll('.output-area').forEach(area => {
            area.className = 'output-area';
            area.textContent = '';
        });
    }

    handleKeyboard(e) {
        // Add keyboard shortcuts if needed
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            // Save settings
        }
    }
}

// Initialize the application
const imageTools = new ImageTools();

// Global functions for onclick handlers
window.compress_image = () => imageTools.compressImage(document.querySelector('[onclick*="compress_image"]').closest('.tool-card'));
window.resize_image = () => imageTools.resizeImage(document.querySelector('[onclick*="resize_image"]').closest('.tool-card'));
window.crop_image = () => imageTools.cropImage(document.querySelector('[onclick*="crop_image"]').closest('.tool-card'));
window.rotate_image = () => imageTools.rotateImage(document.querySelector('[onclick*="rotate_image"]').closest('.tool-card'));
window.convert_image = () => imageTools.convertImage(document.querySelector('[onclick*="convert_image"]').closest('.tool-card'));
window.adjust_brightness = () => imageTools.adjustBrightness(document.querySelector('[onclick*="adjust_brightness"]').closest('.tool-card'));
window.adjust_contrast = () => imageTools.adjustContrast(document.querySelector('[onclick*="adjust_contrast"]').closest('.tool-card'));
window.adjust_saturation = () => imageTools.adjustSaturation(document.querySelector('[onclick*="adjust_saturation"]').closest('.tool-card'));
window.blur_image = () => imageTools.blurImage(document.querySelector('[onclick*="blur_image"]').closest('.tool-card'));
window.sharpen_image = () => imageTools.sharpenImage(document.querySelector('[onclick*="sharpen_image"]').closest('.tool-card'));
window.grayscale_image = () => imageTools.grayscaleImage(document.querySelector('[onclick*="grayscale_image"]').closest('.tool-card'));
window.sepia_image = () => imageTools.sepiaImage(document.querySelector('[onclick*="sepia_image"]').closest('.tool-card'));
window.invert_image = () => imageTools.invertImage(document.querySelector('[onclick*="invert_image"]').closest('.tool-card'));
window.add_watermark = () => imageTools.addWatermark(document.querySelector('[onclick*="add_watermark"]').closest('.tool-card'));
window.batch_process = () => imageTools.batchProcess(document.querySelector('[onclick*="batch_process"]').closest('.tool-card'));
window.save_settings = () => imageTools.saveSettings(document.querySelector('[onclick*="save_settings"]').closest('.settings-panel'));
