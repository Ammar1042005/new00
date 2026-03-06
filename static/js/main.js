// Modern JavaScript for PDF Tools
class PDFTools {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.setupTooltips();
    }

    setupEventListeners() {
        // File input validation
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', (e) => this.validateFileInput(e));
        });

        // Form submissions
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

            // Only validate PDF files strictly, let backend handle Office files
            const fileName = file.name.toLowerCase();
            const fileExt = '.' + fileName.split('.').pop();
            
            if (input.accept.includes('application/pdf') && fileExt !== '.pdf') {
                this.showError(input.parentElement, `File "${file.name}" is not a supported type`);
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
        previewContainer.innerHTML = '<h4>📁 File Preview</h4>';
        
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
            
            // Add preview based on file type
            if (file.type.startsWith('image/') || file.name.toLowerCase().endsWith('.png') || file.name.toLowerCase().endsWith('.jpg') || file.name.toLowerCase().endsWith('.jpeg')) {
                this.createImagePreview(file, fileItem);
            } else if (file.name.toLowerCase().endsWith('.pdf')) {
                this.createPDFPreview(file, fileItem);
            } else {
                this.createDocumentPreview(file, fileItem);
            }
            
            fileList.appendChild(fileItem);
        });

        previewContainer.appendChild(fileList);
        
        // Insert preview after the input
        input.parentElement.insertBefore(previewContainer, input.parentElement.querySelector('.output-area'));
    }

    getFileIcon(fileName) {
        const ext = fileName.toLowerCase().split('.').pop();
        const icons = {
            'pdf': '📄',
            'docx': '📝',
            'xlsx': '📊',
            'pptx': '📈',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️',
            'gif': '🖼️',
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
        
        const img = document.createElement('img');
        img.className = 'preview-image';
        img.style.maxWidth = '200px';
        img.style.maxHeight = '150px';
        img.style.objectFit = 'contain';
        
        const reader = new FileReader();
        reader.onload = (e) => {
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
        
        preview.appendChild(img);
        fileItem.appendChild(preview);
    }

    createPDFPreview(file, fileItem) {
        const preview = document.createElement('div');
        preview.className = 'preview-content';
        
        // Show loading state
        preview.innerHTML = `
            <div class="pdf-preview">
                <div class="pdf-loading">📄 Loading preview...</div>
            </div>
        `;
        
        // Get PDF details from server
        const formData = new FormData();
        formData.append('file', file);
        
        fetch('/pdf-preview', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                preview.innerHTML = `
                    <div class="pdf-preview">
                        <div class="pdf-icon">📄</div>
                        <div class="pdf-info">
                            <div>PDF Document</div>
                            <div>Preview not available</div>
                        </div>
                    </div>
                `;
                return;
            }
            
            preview.innerHTML = `
                <div class="pdf-preview">
                    <img src="${data.thumbnail}" class="pdf-thumbnail" alt="PDF Preview">
                    <div class="pdf-info">
                        <div><strong>${data.page_count}</strong> pages</div>
                        <div>${data.metadata.title || 'Untitled'}</div>
                        <button class="btn-small" onclick="pdfTools.viewPDFDetails('${file.name}', ${file.size}, ${data.page_count})">View Details</button>
                    </div>
                </div>
            `;
        })
        .catch(error => {
            preview.innerHTML = `
                <div class="pdf-preview">
                    <div class="pdf-icon">📄</div>
                    <div class="pdf-info">
                        <div>PDF Document</div>
                        <div>Preview failed</div>
                    </div>
                </div>
            `;
        });
        
        fileItem.appendChild(preview);
    }

    createDocumentPreview(file, fileItem) {
        const preview = document.createElement('div');
        preview.className = 'preview-content';
        
        const ext = file.name.toLowerCase().split('.').pop();
        preview.innerHTML = `
            <div class="doc-preview">
                <div class="doc-icon">${this.getFileIcon(file.name)}</div>
                <div class="doc-info">
                    <div>${ext.toUpperCase()} Document</div>
                    <div>Ready for conversion</div>
                </div>
            </div>
        `;
        
        fileItem.appendChild(preview);
    }

    viewPDFDetails(fileName, fileSize, pageCount = null) {
        const info = `
            <div class="pdf-details">
                <h4>📄 PDF Details</h4>
                <p><strong>File:</strong> ${fileName}</p>
                <p><strong>Size:</strong> ${this.formatFileSize(fileSize)}</p>
                <p><strong>Type:</strong> PDF Document</p>
                ${pageCount ? `<p><strong>Pages:</strong> ${pageCount}</p>` : ''}
                <p><strong>Status:</strong> Ready for processing</p>
            </div>
        `;
        
        // Show in a modal or alert
        alert(info.replace(/<[^>]*>/g, '\n').replace(/&nbsp;/g, ' '));
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
        const toolName = btn.getAttribute('onclick')?.match(/(\w+)\(\)/)?.[1];
        if (!toolName) return;

        switch (toolName) {
            case 'merge':
                await this.mergePDFs(card);
                break;
            case 'split':
                await this.splitPDF(card);
                break;
            case 'rotate':
                await this.rotatePDF(card);
                break;
            case 'watermark':
                await this.watermarkPDF(card);
                break;
            case 'paginate':
                await this.addPageNumbers(card);
                break;
            case 'protect':
                await this.protectPDF(card);
                break;
            case 'unlock':
                await this.unlockPDF(card);
                break;
            case 'compress':
                await this.compressPDF(card);
                break;
            // Add more cases for other tools
            default:
                throw new Error('Unknown tool');
        }
    }

    async mergePDFs(card) {
        const fileInput = card.querySelector('#merge-files');
        const files = fileInput.files;
        
        if (files.length < 2) {
            throw new Error('Please select at least 2 PDF files to merge');
        }

        const formData = new FormData();
        Array.from(files).forEach(file => formData.append('files', file));

        const response = await this.fetchAPI('/merge', {
            method: 'POST',
            body: formData
        });

        this.downloadFile(response, 'merged.pdf');
        this.showSuccess(card.querySelector('.output-area'), 'PDFs merged successfully!');
    }

    async splitPDF(card) {
        const fileInput = card.querySelector('#split-file');
        const fromPage = card.querySelector('#split-from').value;
        const toPage = card.querySelector('#split-to').value;

        if (!fileInput.files[0]) {
            throw new Error('Please select a PDF file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('from', fromPage);
        formData.append('to', toPage);

        const response = await this.fetchAPI('/split', {
            method: 'POST',
            body: formData
        });

        this.downloadFile(response, 'split.pdf');
        this.showSuccess(card.querySelector('.output-area'), 'PDF split successfully!');
    }

    async rotatePDF(card) {
        const fileInput = card.querySelector('#rotate-file');
        const angle = card.querySelector('#rotate-angle').value;
        const pages = card.querySelector('#rotate-pages').value;

        if (!fileInput.files[0]) {
            throw new Error('Please select a PDF file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('angle', angle);
        if (pages) formData.append('pages', pages);

        const response = await this.fetchAPI('/rotate', {
            method: 'POST',
            body: formData
        });

        this.downloadFile(response, 'rotated.pdf');
        this.showSuccess(card.querySelector('.output-area'), 'PDF rotated successfully!');
    }

    async watermarkPDF(card) {
        const fileInput = card.querySelector('#wm-file');
        const text = card.querySelector('#wm-text').value;
        const opacity = card.querySelector('#wm-opacity').value;
        const fontSize = card.querySelector('#wm-font').value;

        if (!fileInput.files[0] || !text) {
            throw new Error('Please select a PDF file and enter watermark text');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('text', text);
        formData.append('opacity', opacity);
        formData.append('font_size', fontSize);

        const response = await this.fetchAPI('/watermark', {
            method: 'POST',
            body: formData
        });

        this.downloadFile(response, 'watermarked.pdf');
        this.showSuccess(card.querySelector('.output-area'), 'Watermark added successfully!');
    }

    async addPageNumbers(card) {
        const fileInput = card.querySelector('#pg-file');
        const position = card.querySelector('#pg-pos').value;
        const fontSize = card.querySelector('#pg-font').value;

        if (!fileInput.files[0]) {
            throw new Error('Please select a PDF file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('position', position);
        formData.append('font_size', fontSize);

        const response = await this.fetchAPI('/paginate', {
            method: 'POST',
            body: formData
        });

        this.downloadFile(response, 'numbered.pdf');
        this.showSuccess(card.querySelector('.output-area'), 'Page numbers added successfully!');
    }

    async protectPDF(card) {
        const fileInput = card.querySelector('#prot-file');
        const userPassword = card.querySelector('#prot-user').value;
        const ownerPassword = card.querySelector('#prot-owner').value;

        if (!fileInput.files[0] || !userPassword) {
            throw new Error('Please select a PDF file and enter a user password');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('user_password', userPassword);
        if (ownerPassword) formData.append('owner_password', ownerPassword);

        const response = await this.fetchAPI('/protect', {
            method: 'POST',
            body: formData
        });

        this.downloadFile(response, 'protected.pdf');
        this.showSuccess(card.querySelector('.output-area'), 'PDF protected successfully!');
    }

    async unlockPDF(card) {
        const fileInput = card.querySelector('#unl-file');
        const password = card.querySelector('#unl-pass').value;

        if (!fileInput.files[0] || !password) {
            throw new Error('Please select a PDF file and enter the password');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('password', password);

        const response = await this.fetchAPI('/unlock', {
            method: 'POST',
            body: formData
        });

        this.downloadFile(response, 'unlocked.pdf');
        this.showSuccess(card.querySelector('.output-area'), 'PDF unlocked successfully!');
    }

    async compressPDF(card) {
        const fileInput = card.querySelector('#cmp-file');

        if (!fileInput.files[0]) {
            throw new Error('Please select a PDF file');
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await this.fetchAPI('/compress', {
            method: 'POST',
            body: formData
        });

        this.downloadFile(response, 'compressed.pdf');
        this.showSuccess(card.querySelector('.output-area'), 'PDF compressed successfully!');
    }

    async fetchAPI(url, options) {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Request failed');
        }

        return response.blob();
    }

    downloadFile(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    setButtonLoading(btn, loading) {
        if (loading) {
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> Processing...';
        } else {
            btn.disabled = false;
            btn.innerHTML = btn.getAttribute('data-original-text') || 'Process';
        }
    }

    showError(container, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        container.appendChild(errorDiv);
    }

    showSuccess(container, message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        container.appendChild(successDiv);
    }

    clearMessages(container) {
        container.querySelectorAll('.error-message, .success-message').forEach(msg => msg.remove());
    }

    async loadSettings() {
        try {
            const response = await fetch('/settings');
            const data = await response.json();
            // Store settings for later use
            this.settings = data.config;
        } catch (error) {
            console.warn('Could not load settings:', error);
        }
    }

    setupTooltips() {
        // Add tooltips for better UX
        document.querySelectorAll('[title]').forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.getAttribute('title'));
            });
            
            element.addEventListener('mouseleave', (e) => {
                this.hideTooltip();
            });
        });
    }

    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: #333;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
            pointer-events: none;
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
        
        this.currentTooltip = tooltip;
    }

    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }

    handleKeyboard(e) {
        // Ctrl+Enter to submit the focused form
        if (e.ctrlKey && e.key === 'Enter') {
            const activeElement = document.activeElement;
            const card = activeElement.closest('.tool-card');
            if (card) {
                const btn = card.querySelector('.btn');
                if (btn && !btn.disabled) {
                    btn.click();
                }
            }
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new PDFTools();
});

// Global functions for backward compatibility
function merge() { /* Handled by PDFTools class */ }
function split() { /* Handled by PDFTools class */ }
function rotate() { /* Handled by PDFTools class */ }
function watermark() { /* Handled by PDFTools class */ }
function paginate() { /* Handled by PDFTools class */ }
function protect() { /* Handled by PDFTools class */ }
function unlock() { /* Handled by PDFTools class */ }
function compress() { /* Handled by PDFTools class */ }
