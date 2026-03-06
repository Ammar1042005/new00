class CanvasImageEditor {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.originalImage = null;
        this.currentImage = null;
        this.history = [];
        this.historyStep = -1;
        this.isDragging = false;
        this.cropStart = null;
        this.cropEnd = null;
        this.watermarkPosition = { x: 50, y: 50 };
        this.isDraggingWatermark = false;
        this.tempCanvas = document.createElement('canvas');
        this.tempCtx = this.tempCanvas.getContext('2d');
    }

    loadImage(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    this.originalImage = img;
                    this.currentImage = img;
                    this.resetCanvas();
                    this.saveToHistory();
                    resolve(img);
                };
                img.onerror = reject;
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        });
    }

    resetCanvas() {
        if (!this.originalImage) return;
        
        // Set canvas size to match original image
        this.canvas.width = this.originalImage.width;
        this.canvas.height = this.originalImage.height;
        this.tempCanvas.width = this.originalImage.width;
        this.tempCanvas.height = this.originalImage.height;
        
        // Draw ORIGINAL image (not currentImage)
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(this.originalImage, 0, 0);
    }

    saveToHistory() {
        // Remove any states after current step
        this.history = this.history.slice(0, this.historyStep + 1);
        
        // Save current state
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        this.history.push(imageData);
        this.historyStep++;
        
        // Limit history to 20 states
        if (this.history.length > 20) {
            this.history.shift();
            this.historyStep--;
        }
    }

    undo() {
        if (this.historyStep > 0) {
            this.historyStep--;
            this.ctx.putImageData(this.history[this.historyStep], 0, 0);
            // Update current image from canvas
            this.updateCurrentImageFromCanvas();
        }
    }

    redo() {
        if (this.historyStep < this.history.length - 1) {
            this.historyStep++;
            this.ctx.putImageData(this.history[this.historyStep], 0, 0);
            // Update current image from canvas
            this.updateCurrentImageFromCanvas();
        }
    }

    updateCurrentImageFromCanvas() {
        const tempImg = new Image();
        tempImg.onload = () => {
            this.currentImage = tempImg;
        };
        tempImg.src = this.canvas.toDataURL();
    }

    flip(horizontal = true) {
        if (!this.currentImage) return;
        
        // Work on current canvas state, not original
        this.ctx.save();
        if (horizontal) {
            this.ctx.scale(-1, 1);
            this.ctx.drawImage(this.currentImage, -this.canvas.width, 0);
        } else {
            this.ctx.scale(1, -1);
            this.ctx.drawImage(this.currentImage, 0, -this.canvas.height);
        }
        this.ctx.restore();
        
        // Update current image
        this.updateCurrentImageFromCanvas();
        this.saveToHistory();
    }
    resize(width, height, maintainAspect = true) {
        if (!this.originalImage) return;
        
        let newWidth = width;
        let newHeight = height;
        
        if (maintainAspect) {
            const aspectRatio = this.originalImage.width / this.originalImage.height;
            if (width / height > aspectRatio) {
                newWidth = height * aspectRatio;
            } else {
                newHeight = width / aspectRatio;
            }
        }
        
        this.canvas.width = newWidth;
        this.canvas.height = newHeight;
        this.ctx.drawImage(this.originalImage, 0, 0, newWidth, newHeight);
        
        // Update current and original images
        this.updateCurrentImageFromCanvas();
        const tempImg = new Image();
        tempImg.onload = () => {
            this.originalImage = tempImg;
        };
        tempImg.src = this.canvas.toDataURL();
        
        this.saveToHistory();
    }

    rotate(angle) {
        if (!this.currentImage) return;
        
        const radians = angle * Math.PI / 180;
        const sin = Math.abs(Math.sin(radians));
        const cos = Math.abs(Math.cos(radians));
        
        // Calculate new dimensions based on CURRENT image, not original
        const newWidth = this.currentImage.width * cos + this.currentImage.height * sin;
        const newHeight = this.currentImage.width * sin + this.currentImage.height * cos;
        
        this.tempCanvas.width = newWidth;
        this.tempCanvas.height = newHeight;
        
        this.tempCtx.translate(newWidth / 2, newHeight / 2);
        this.tempCtx.rotate(radians);
        this.tempCtx.drawImage(this.currentImage, -this.currentImage.width / 2, -this.currentImage.height / 2);
        
        this.canvas.width = newWidth;
        this.canvas.height = newHeight;
        this.ctx.drawImage(this.tempCanvas, 0, 0);
        
        // Update current image
        this.updateCurrentImageFromCanvas();
        this.saveToHistory();
    }

    adjustBrightness(factor) {
        if (!this.currentImage) return;
        
        // Always work from the original image for adjustments
        // This ensures 100% always returns to the original state
        this.ctx.drawImage(this.originalImage, 0, 0);
        
        // Factor is already normalized (0-2 range where 1.0 = 100% = normal)
        if (factor !== 1.0) {  // Only apply adjustment if not at normal
            const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
            const data = imageData.data;
            
            for (let i = 0; i < data.length; i += 4) {
                // Apply brightness adjustment by adding/subtracting from pixel values
                const adjustment = (factor - 1.0) * 128; // Scale adjustment to reasonable range
                
                data[i] = Math.min(255, Math.max(0, data[i] + adjustment));     // Red
                data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + adjustment)); // Green
                data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + adjustment)); // Blue
            }
            
            this.ctx.putImageData(imageData, 0, 0);
        }
        
        // Update current image to reflect the new state
        this.updateCurrentImageFromCanvas();
        this.saveToHistory();
    }

    adjustContrast(factor) {
        if (!this.currentImage) return;
        
        // Always work from the original image for adjustments
        // This ensures 100% always returns to the original state
        this.ctx.drawImage(this.originalImage, 0, 0);
        
        // Factor is already normalized (0-2 range where 1.0 = 100% = normal)
        if (factor !== 1.0) {  // Only apply adjustment if not at normal
            const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
            const data = imageData.data;
            
            for (let i = 0; i < data.length; i += 4) {
                // Apply contrast adjustment relative to normal (100% = no change)
                data[i] = Math.min(255, Math.max(0, (data[i] - 128) * factor + 128));     // Red
                data[i + 1] = Math.min(255, Math.max(0, (data[i + 1] - 128) * factor + 128)); // Green
                data[i + 2] = Math.min(255, Math.max(0, (data[i + 2] - 128) * factor + 128)); // Blue
            }
            
            this.ctx.putImageData(imageData, 0, 0);
        }
        
        // Update current image to reflect the new state
        this.updateCurrentImageFromCanvas();
        this.saveToHistory();
    }

    adjustSaturation(factor) {
        if (!this.currentImage) return;
        
        // Always work from the original image for adjustments
        // This ensures 100% always returns to the original state
        this.ctx.drawImage(this.originalImage, 0, 0);
        
        // Factor is already normalized (0-2 range where 1.0 = 100% = normal)
        if (factor !== 1.0) {  // Only apply adjustment if not at normal
            const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
            const data = imageData.data;
            
            for (let i = 0; i < data.length; i += 4) {
                const gray = 0.2989 * data[i] + 0.5870 * data[i + 1] + 0.1140 * data[i + 2];
                // Apply saturation adjustment relative to normal (100% = no change)
                data[i] = Math.min(255, Math.max(0, gray + factor * (data[i] - gray)));     // Red
                data[i + 1] = Math.min(255, Math.max(0, gray + factor * (data[i + 1] - gray))); // Green
                data[i + 2] = Math.min(255, Math.max(0, gray + factor * (data[i + 2] - gray))); // Blue
            }
            
            this.ctx.putImageData(imageData, 0, 0);
        }
        
        // Update current image to reflect the new state
        this.updateCurrentImageFromCanvas();
        this.saveToHistory();
    }

    grayscale() {
        if (!this.currentImage) return;
        
        // Work on current canvas state, not original
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const data = imageData.data;
        
        for (let i = 0; i < data.length; i += 4) {
            const gray = 0.2989 * data[i] + 0.5870 * data[i + 1] + 0.1140 * data[i + 2];
            data[i] = gray;     // Red
            data[i + 1] = gray; // Green
            data[i + 2] = gray; // Blue
        }
        
        this.ctx.putImageData(imageData, 0, 0);
        this.saveToHistory();
    }

    sepia() {
        if (!this.currentImage) return;
        
        // Work on current canvas state, not original
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const data = imageData.data;
        
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            
            data[i] = Math.min(255, (r * 0.393) + (g * 0.769) + (b * 0.189));     // Red
            data[i + 1] = Math.min(255, (r * 0.349) + (g * 0.686) + (b * 0.168)); // Green
            data[i + 2] = Math.min(255, (r * 0.272) + (g * 0.534) + (b * 0.131)); // Blue
        }
        
        this.ctx.putImageData(imageData, 0, 0);
        this.saveToHistory();
    }

    invert() {
        if (!this.currentImage) return;
        
        // Work on current canvas state, not original
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const data = imageData.data;
        
        for (let i = 0; i < data.length; i += 4) {
            data[i] = 255 - data[i];         // Red
            data[i + 1] = 255 - data[i + 1]; // Green
            data[i + 2] = 255 - data[i + 2]; // Blue
        }
        
        this.ctx.putImageData(imageData, 0, 0);
        this.saveToHistory();
    }

    blur(radius) {
        if (!this.currentImage) return;
        
        // Work on current canvas state, not original
        this.ctx.filter = `blur(${radius}px)`;
        this.ctx.drawImage(this.canvas, 0, 0);
        this.ctx.filter = 'none';
        this.saveToHistory();
    }

    sharpen() {
        if (!this.currentImage) return;
        
        // Work on current canvas state, not original
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const data = imageData.data;
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        const output = new Uint8ClampedArray(data);
        
        // Sharpen kernel
        const kernel = [
            0, -1, 0,
            -1, 5, -1,
            0, -1, 0
        ];
        
        for (let y = 1; y < height - 1; y++) {
            for (let x = 1; x < width - 1; x++) {
                for (let c = 0; c < 3; c++) {
                    let sum = 0;
                    for (let ky = -1; ky <= 1; ky++) {
                        for (let kx = -1; kx <= 1; kx++) {
                            const pixelIndex = ((y + ky) * width + (x + kx)) * 4 + c;
                            const kernelIndex = (ky + 1) * 3 + (kx + 1);
                            sum += data[pixelIndex] * kernel[kernelIndex];
                        }
                    }
                    output[(y * width + x) * 4 + c] = Math.min(255, Math.max(0, sum));
                }
            }
        }
        
        const outputImageData = new ImageData(output, width, height);
        this.ctx.putImageData(outputImageData, 0, 0);
        this.saveToHistory();
    }

    // Crop functionality
    startCropMode() {
        this.canvas.style.cursor = 'crosshair';
        this.canvas.onclick = (e) => this.handleCropClick(e);
        this.canvas.onmousemove = (e) => this.handleCropMove(e);
    }

    stopCropMode() {
        this.canvas.style.cursor = 'default';
        this.canvas.onclick = null;
        this.canvas.onmousemove = null;
        this.cropStart = null;
        this.cropEnd = null;
    }

    handleCropClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (this.canvas.width / rect.width);
        const y = (e.clientY - rect.top) * (this.canvas.height / rect.height);
        
        if (!this.cropStart) {
            this.cropStart = { x, y };
        } else {
            this.cropEnd = { x, y };
            this.applyCrop();
        }
    }

    handleCropMove(e) {
        if (!this.cropStart) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (this.canvas.width / rect.width);
        const y = (e.clientY - rect.top) * (this.canvas.height / rect.height);
        
        // Draw crop selection
        this.resetCanvas();
        this.ctx.strokeStyle = '#667eea';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);
        this.ctx.strokeRect(
            this.cropStart.x,
            this.cropStart.y,
            x - this.cropStart.x,
            y - this.cropStart.y
        );
        this.ctx.setLineDash([]);
    }

    applyCrop() {
        if (!this.cropStart || !this.cropEnd) return;
        
        const x = Math.min(this.cropStart.x, this.cropEnd.x);
        const y = Math.min(this.cropStart.y, this.cropEnd.y);
        const width = Math.abs(this.cropEnd.x - this.cropStart.x);
        const height = Math.abs(this.cropEnd.y - this.cropStart.y);
        
        const imageData = this.ctx.getImageData(x, y, width, height);
        
        this.canvas.width = width;
        this.canvas.height = height;
        this.ctx.putImageData(imageData, 0, 0);
        
        // Update original and current images
        this.updateCurrentImageFromCanvas();
        const tempImg = new Image();
        tempImg.onload = () => {
            this.originalImage = tempImg;
        };
        tempImg.src = this.canvas.toDataURL();
        
        this.saveToHistory();
        this.stopCropMode();
    }

    // Watermark functionality
    addWatermark(text, position = 'bottom-right') {
        if (!this.originalImage) return;
        
        // Start with current canvas state
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        tempCanvas.width = this.canvas.width;
        tempCanvas.height = this.canvas.height;
        tempCtx.drawImage(this.canvas, 0, 0);
        
        this.ctx.font = '20px Arial';
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.8)';
        this.ctx.lineWidth = 1;
        
        const metrics = this.ctx.measureText(text);
        const textWidth = metrics.width;
        const textHeight = 20;
        const padding = 10;
        
        let x, y;
        
        switch (position) {
            case 'top-left':
                x = padding;
                y = textHeight + padding;
                break;
            case 'top-right':
                x = this.canvas.width - textWidth - padding;
                y = textHeight + padding;
                break;
            case 'center':
                x = (this.canvas.width - textWidth) / 2;
                y = (this.canvas.height + textHeight) / 2;
                break;
            case 'bottom-left':
                x = padding;
                y = this.canvas.height - padding;
                break;
            case 'bottom-right':
            default:
                x = this.canvas.width - textWidth - padding;
                y = this.canvas.height - padding;
                break;
        }
        
        // Draw background
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        this.ctx.fillRect(x - padding/2, y - textHeight - padding/2, textWidth + padding, textHeight + padding);
        
        // Draw text
        this.ctx.fillStyle = 'white';
        this.ctx.fillText(text, x, y);
        this.ctx.strokeText(text, x, y);
        
        this.saveToHistory();
    }

    // Export functionality
    export(format = 'png', quality = 0.9) {
        const mimeType = format === 'jpg' ? 'image/jpeg' : `image/${format}`;
        return this.canvas.toDataURL(mimeType, quality);
    }

    getBlob(format = 'png', quality = 0.9) {
        return new Promise(resolve => {
            this.canvas.toBlob(resolve, `image/${format}`, quality);
        });
    }

    reset() {
        if (!this.originalImage) return;
        
        // Reset to the very first original loaded image
        this.currentImage = this.originalImage;
        this.resetCanvas();
        this.saveToHistory();
    }

    removeBackground(strength = 'moderate', preserveEdges = true) {
        if (!this.currentImage) return;
        
        // Work on current canvas state
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const data = imageData.data;
        
        // Set thresholds based on strength
        let threshold, varianceThreshold;
        switch(strength) {
            case 'conservative':
                threshold = 220;
                varianceThreshold = 20;
                break;
            case 'moderate':
                threshold = 200;
                varianceThreshold = 30;
                break;
            case 'aggressive':
                threshold = 180;
                varianceThreshold = 40;
                break;
            default:
                threshold = 200;
                varianceThreshold = 30;
        }
        
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            
            // Calculate brightness and color variance
            const brightness = (r + g + b) / 3;
            const colorVariance = Math.abs(r - g) + Math.abs(g - b) + Math.abs(r - b);
            
            // Check if pixel should be removed
            let shouldRemove = brightness > threshold && colorVariance < varianceThreshold;
            
            // Additional edge preservation logic
            if (preserveEdges && shouldRemove) {
                // Check neighboring pixels for edge detection
                const pixelIndex = i / 4;
                const x = pixelIndex % this.canvas.width;
                const y = Math.floor(pixelIndex / this.canvas.width);
                
                // Simple edge detection - check if neighbors are very different
                let isEdge = false;
                for (let dy = -1; dy <= 1; dy++) {
                    for (let dx = -1; dx <= 1; dx++) {
                        if (dx === 0 && dy === 0) continue;
                        
                        const nx = x + dx;
                        const ny = y + dy;
                        
                        if (nx >= 0 && nx < this.canvas.width && ny >= 0 && ny < this.canvas.height) {
                            const neighborIndex = (ny * this.canvas.width + nx) * 4;
                            const nr = data[neighborIndex];
                            const ng = data[neighborIndex + 1];
                            const nb = data[neighborIndex + 2];
                            
                            const neighborBrightness = (nr + ng + nb) / 3;
                            if (Math.abs(brightness - neighborBrightness) > 50) {
                                isEdge = true;
                                break;
                            }
                        }
                    }
                    if (isEdge) break;
                }
                
                shouldRemove = !isEdge;
            }
            
            // Apply background removal
            if (shouldRemove) {
                data[i] = 255;     // Red
                data[i + 1] = 255; // Green
                data[i + 2] = 255; // Blue
            }
        }
        
        this.ctx.putImageData(imageData, 0, 0);
        this.saveToHistory();
    }

    removeColorBrush(hexColor, tolerance = 30, brushSize = 10) {
        if (!this.currentImage) return;
        
        // Convert hex color to RGB
        const r = parseInt(hexColor.substr(1, 2), 16);
        const g = parseInt(hexColor.substr(3, 2), 16);
        const b = parseInt(hexColor.substr(5, 2), 16);
        
        // Work on current canvas state
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const data = imageData.data;
        
        for (let i = 0; i < data.length; i += 4) {
            const pixelR = data[i];
            const pixelG = data[i + 1];
            const pixelB = data[i + 2];
            
            // Calculate color distance
            const colorDistance = Math.sqrt(
                Math.pow(pixelR - r, 2) +
                Math.pow(pixelG - g, 2) +
                Math.pow(pixelB - b, 2)
            );
            
            // Remove pixels within tolerance range
            if (colorDistance <= tolerance * 2.55) { // Convert tolerance (0-100) to RGB scale (0-255)
                data[i] = 255;     // Red
                data[i + 1] = 255; // Green
                data[i + 2] = 255; // Blue
            }
        }
        
        this.ctx.putImageData(imageData, 0, 0);
        this.saveToHistory();
    }

    paintBrushRemove(x, y, hexColor, tolerance = 30, brushSize = 10) {
        if (!this.currentImage) return;
        
        // Convert hex color to RGB
        const r = parseInt(hexColor.substr(1, 2), 16);
        const g = parseInt(hexColor.substr(3, 2), 16);
        const b = parseInt(hexColor.substr(5, 2), 16);
        
        // Work on current canvas state
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const data = imageData.data;
        
        // Calculate brush area
        const radius = brushSize / 2;
        const startX = Math.max(0, Math.floor(x - radius));
        const endX = Math.min(this.canvas.width, Math.ceil(x + radius));
        const startY = Math.max(0, Math.floor(y - radius));
        const endY = Math.min(this.canvas.height, Math.ceil(y + radius));
        
        // Process pixels in brush area
        for (let py = startY; py < endY; py++) {
            for (let px = startX; px < endX; px++) {
                // Check if pixel is within brush circle
                const distance = Math.sqrt(Math.pow(px - x, 2) + Math.pow(py - y, 2));
                if (distance <= radius) {
                    const pixelIndex = (py * this.canvas.width + px) * 4;
                    const pixelR = data[pixelIndex];
                    const pixelG = data[pixelIndex + 1];
                    const pixelB = data[pixelIndex + 2];
                    
                    // Calculate color distance
                    const colorDistance = Math.sqrt(
                        Math.pow(pixelR - r, 2) +
                        Math.pow(pixelG - g, 2) +
                        Math.pow(pixelB - b, 2)
                    );
                    
                    // Remove pixels within tolerance range
                    if (colorDistance <= tolerance * 2.55) { // Convert tolerance (0-100) to RGB scale (0-255)
                        data[pixelIndex] = 255;     // Red
                        data[pixelIndex + 1] = 255; // Green
                        data[pixelIndex + 2] = 255; // Blue
                    }
                }
            }
        }
        
        this.ctx.putImageData(imageData, 0, 0);
        // Don't save to history on every brush stroke - only on mouse up
    }

    saveBrushStroke() {
        // Call this when mouse is released to save the complete brush stroke to history
        this.saveToHistory();
    }

    upscale(scaleFactor = 2) {
        if (!this.currentImage) return;
        
        const newWidth = Math.round(this.currentImage.width * scaleFactor);
        const newHeight = Math.round(this.currentImage.height * scaleFactor);
        
        // Create a temporary canvas for upscaling
        const upscaleCanvas = document.createElement('canvas');
        const upscaleCtx = upscaleCanvas.getContext('2d');
        upscaleCanvas.width = newWidth;
        upscaleCanvas.height = newHeight;
        
        // Use image smoothing for better quality
        upscaleCtx.imageSmoothingEnabled = true;
        upscaleCtx.imageSmoothingQuality = 'high';
        
        // Draw the scaled image
        upscaleCtx.drawImage(this.currentImage, 0, 0, newWidth, newHeight);
        
        // Update main canvas
        this.canvas.width = newWidth;
        this.canvas.height = newHeight;
        this.ctx.drawImage(upscaleCanvas, 0, 0);
        
        // Update current image
        this.updateCurrentImageFromCanvas();
        this.saveToHistory();
    }
}
