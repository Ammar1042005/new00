// Modern JavaScript for PdfSwiss
document.addEventListener('DOMContentLoaded', function() {
    // Initialize functionality
    initializeFilters();
    initializeMobileMenu();
    initializeScrollAnimations();
    initializeFileUploads();
    initializeTooltips();
    
    // Load settings after 1 second
    setTimeout(() => {
        load_settings();
    }, 1000);
});

// Filter functionality
function initializeFilters() {
    const filterTabs = document.querySelectorAll('.filter-tab');
    const toolCards = document.querySelectorAll('.tool-card');
    
    filterTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const filter = this.dataset.filter;
            
            // Update active tab
            filterTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Filter tools
            toolCards.forEach(card => {
                const category = card.dataset.category;
                if (filter === 'all' || category === filter) {
                    card.classList.remove('hidden');
                    card.style.animation = 'fadeInUp 0.6s ease-out';
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });
}

// Mobile menu
function initializeMobileMenu() {
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
}

// Scroll animations
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements
    document.querySelectorAll('.tool-card, .settings-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// File upload functionality
function initializeFileUploads() {
    const fileUploads = document.querySelectorAll('.file-upload');
    
    fileUploads.forEach(upload => {
        const input = upload.querySelector('.file-input');
        const label = upload.querySelector('.file-label');
        
        if (input && label) {
            input.addEventListener('change', function(e) {
                const files = e.target.files;
                if (files.length > 0) {
                    const fileNames = Array.from(files).map(f => f.name).join(', ');
                    label.querySelector('.file-text').textContent = fileNames;
                    upload.style.borderColor = 'var(--success)';
                    upload.style.background = 'rgba(16, 185, 129, 0.1)';
                }
            });
            
            // Drag and drop
            upload.addEventListener('dragover', function(e) {
                e.preventDefault();
                upload.style.borderColor = 'var(--primary-color)';
                upload.style.background = 'rgba(99, 102, 241, 0.05)';
            });
            
            upload.addEventListener('dragleave', function(e) {
                e.preventDefault();
                upload.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                upload.style.background = 'var(--surface-light)';
            });
            
            upload.addEventListener('drop', function(e) {
                e.preventDefault();
                input.files = e.dataTransfer.files;
                const event = new Event('change', { bubbles: true });
                input.dispatchEvent(event);
            });
        }
    });
}

// Tool functions
function merge() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('merge-files');
    
    if (!fileInput.files || fileInput.files.length < 2) {
        showToast('Please select at least 2 PDF files', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    for (let file of fileInput.files) {
        formData.append('files', file);
    }
    
    fetch('/merge', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'merged.pdf');
        showToast('PDFs merged successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function split() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('split-file');
    const fromPage = document.getElementById('split-from').value;
    const toPage = document.getElementById('split-to').value;
    
    if (!fileInput.files[0]) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('from', fromPage);
    formData.append('to', toPage);
    
    fetch('/split', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'split.pdf');
        showToast('PDF split successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function compress() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('cmp-file');
    
    if (!fileInput.files[0]) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    fetch('/compress', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'compressed.pdf');
        showToast('PDF compressed successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function word_to_pdf() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('word-file');
    
    if (!fileInput.files[0]) {
        showToast('Please select a Word file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    fetch('/word-to-pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'converted.pdf');
        showToast('Word document converted to PDF!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function pdf_to_word() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('pdf-word-file');
    
    if (!fileInput.files[0]) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    fetch('/pdf-to-word', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'converted.docx');
        showToast('PDF converted to Word document!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function ocr() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('ocr-file');
    const dpi = document.getElementById('ocr-dpi').value;
    
    if (!fileInput.files[0]) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('dpi', dpi);
    
    fetch('/ocr', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'ocr.pdf');
        showToast('OCR applied successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function rotate() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('rotate-file');
    const angle = document.getElementById('rotate-angle').value;
    
    if (!fileInput.files[0]) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('angle', angle);
    
    fetch('/rotate', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'rotated.pdf');
        showToast('PDF rotated successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function watermark() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('watermark-file');
    const text = document.getElementById('watermark-text').value;
    const fontSize = document.getElementById('watermark-font').value;
    
    if (!fileInput.files[0] || !text) {
        showToast('Please select a PDF file and enter watermark text', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('text', text);
    formData.append('font_size', fontSize);
    
    fetch('/watermark', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'watermarked.pdf');
        showToast('Watermark added successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function protect() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('protect-file');
    const userPass = document.getElementById('prot-user').value;
    const ownerPass = document.getElementById('prot-owner').value;
    
    if (!fileInput.files[0] || !userPass) {
        showToast('Please select a PDF file and enter user password', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('user_password', userPass);
    formData.append('owner_password', ownerPass);
    
    fetch('/protect', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'protected.pdf');
        showToast('PDF protected successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function unlock() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('unlock-file');
    const password = document.getElementById('unl-pass').value;
    
    if (!fileInput.files[0] || !password) {
        showToast('Please select a PDF file and enter password', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('password', password);
    
    fetch('/unlock', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'unlocked.pdf');
        showToast('PDF unlocked successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function excel_to_pdf() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('excel-file');
    
    if (!fileInput.files[0]) {
        showToast('Please select an Excel file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    fetch('/excel-to-pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'converted.pdf');
        showToast('Excel spreadsheet converted to PDF!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function pptx_to_pdf() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('pptx-file');
    
    if (!fileInput.files[0]) {
        showToast('Please select a PowerPoint file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    fetch('/pptx-to-pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'converted.pdf');
        showToast('PowerPoint presentation converted to PDF!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function pdf_to_excel() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('pdf-excel-file');
    
    if (!fileInput.files[0]) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    fetch('/pdf-to-excel', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'converted.xlsx');
        showToast('PDF converted to Excel spreadsheet!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function pdf_to_pptx() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('pdf-pptx-file');
    
    if (!fileInput.files[0]) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    fetch('/pdf-to-pptx', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'converted.pptx');
        showToast('PDF converted to PowerPoint presentation!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function images_to_pdf() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('images-files');
    
    if (!fileInput.files || fileInput.files.length < 1) {
        showToast('Please select at least 1 image file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    for (let file of fileInput.files) {
        formData.append('files', file);
    }
    
    fetch('/images-to-pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'converted.pdf');
        showToast('Images converted to PDF!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function pdf_to_images() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('pdf-images-file');
    const format = document.getElementById('pdf-img-format').value;
    const dpi = document.getElementById('pdf-img-dpi').value;
    
    if (!fileInput.files[0]) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('format', format);
    formData.append('dpi', dpi);
    
    fetch('/pdf-to-images', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'images.zip');
        showToast('PDF converted to images!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function paginate() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('paginate-file');
    const fontSize = document.getElementById('pg-font').value;
    
    if (!fileInput.files[0]) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('font_size', fontSize);
    
    fetch('/paginate', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'paginated.pdf');
        showToast('Page numbers added successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function reorder() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('reorder-file');
    const order = document.getElementById('reorder-order').value;
    
    if (!fileInput.files[0] || !order) {
        showToast('Please select a PDF file and enter page order', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('order', order);
    
    fetch('/reorder', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'reordered.pdf');
        showToast('Pages reordered successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function remove_pages() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('remove-file');
    const pages = document.getElementById('remove-pages').value;
    
    if (!fileInput.files[0] || !pages) {
        showToast('Please select a PDF file and enter pages to remove', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('pages', pages);
    
    fetch('/remove-pages', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'removed.pdf');
        showToast('Pages removed successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function extract_images() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('extract-images-file');
    
    if (!fileInput.files[0]) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    fetch('/extract-images', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'images.zip');
        showToast('Images extracted successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function batch_process() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('batch-files');
    const operation = document.getElementById('batch-operation').value;
    
    if (!fileInput.files || fileInput.files.length < 1) {
        showToast('Please select at least 1 file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    for (let file of fileInput.files) {
        formData.append('files', file);
    }
    formData.append('operation', operation);
    
    // Add additional parameters based on operation
    if (operation === 'compress_strong') {
        formData.append('quality', 'screen');
    } else if (operation === 'ocr') {
        formData.append('dpi', '200');
    } else if (operation === 'pdf_to_images') {
        formData.append('format', 'png');
        formData.append('dpi', '200');
    }
    
    fetch('/batch', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'batch_results.zip');
        showToast('Batch processing completed!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function edit_metadata() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput = document.getElementById('metadata-file');
    const title = document.getElementById('metadata-title').value;
    const author = document.getElementById('metadata-author').value;
    const subject = document.getElementById('metadata-subject').value;
    const keywords = document.getElementById('metadata-keywords').value;
    
    if (!fileInput.files[0]) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('title', title);
    formData.append('author', author);
    formData.append('subject', subject);
    formData.append('keywords', keywords);
    
    fetch('/edit-metadata', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'metadata_edited.pdf');
        showToast('Metadata edited successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

function compare_pdfs() {
    const button = event.target.closest('.btn');
    const originalText = button.querySelector('.btn-text').textContent;
    const fileInput1 = document.getElementById('compare-file1');
    const fileInput2 = document.getElementById('compare-file2');
    
    if (!fileInput1.files[0] || !fileInput2.files[0]) {
        showToast('Please select both PDF files', 'error');
        return;
    }
    
    showLoading(button);
    
    const formData = new FormData();
    formData.append('file1', fileInput1.files[0]);
    formData.append('file2', fileInput2.files[0]);
    
    fetch('/compare', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) return response.json();
        return response.blob();
    })
    .then(result => {
        hideLoading(button, originalText);
        if (result.error) {
            throw new Error(result.error);
        }
        downloadFile(result, 'comparison.pdf');
        showToast('PDFs compared successfully!', 'success');
    })
    .catch(error => {
        hideLoading(button, originalText);
        showToast(error.message, 'error');
    });
}

// Settings Functions
function save_settings() {
    const tesseractPath = document.getElementById('tesseract-path').value;
    const libreofficePath = document.getElementById('libreoffice-path').value;
    const ghostscriptPath = document.getElementById('ghostscript-path').value;
    
    // Save to backend
    const formData = new FormData();
    formData.append('tesseract_path', tesseractPath);
    formData.append('libreoffice_path', libreofficePath);
    formData.append('ghostscript_path', ghostscriptPath);
    
    fetch('/settings', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Also save to localStorage as backup
        const settings = {
            tesseract: tesseractPath,
            libreoffice: libreofficePath,
            ghostscript: ghostscriptPath
        };
        localStorage.setItem('pdfswiss-settings', JSON.stringify(settings));
        
        showToast('Settings saved successfully!', 'success');
    })
    .catch(error => {
        showToast('Failed to save settings: ' + error.message, 'error');
    });
}

function load_settings() {
    // Load from backend first
    fetch('/settings')
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            throw new Error(result.error);
        }
        
        const config = result.config;
        document.getElementById('tesseract-path').value = config.tesseract_path || '';
        document.getElementById('libreoffice-path').value = config.libreoffice_path || '';
        document.getElementById('ghostscript-path').value = config.ghostscript_path || '';
        
        // Also save to localStorage as backup
        const settings = {
            tesseract: config.tesseract_path || '',
            libreoffice: config.libreoffice_path || '',
            ghostscript: config.ghostscript_path || ''
        };
        localStorage.setItem('pdfswiss-settings', JSON.stringify(settings));
        
        showToast('Settings loaded successfully!', 'success');
    })
    .catch(error => {
        // Fallback to localStorage if backend fails
        const savedSettings = localStorage.getItem('pdfswiss-settings');
        
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            
            document.getElementById('tesseract-path').value = settings.tesseract || '';
            document.getElementById('libreoffice-path').value = settings.libreoffice || '';
            document.getElementById('ghostscript-path').value = settings.ghostscript || '';
            
            showToast('Settings loaded from local storage!', 'success');
        } else {
            showToast('No saved settings found!', 'error');
        }
    });
}

// Utility functions
function showLoading(button) {
    button.classList.add('loading');
    button.disabled = true;
    button.querySelector('.btn-text').textContent = 'Processing...';
}

function hideLoading(button, originalText) {
    button.classList.remove('loading');
    button.disabled = false;
    button.querySelector('.btn-text').textContent = originalText;
}

function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function showToast(message, type = 'info') {
    // Remove existing toast
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create new toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-title">${type === 'success' ? 'Success' : type === 'error' ? 'Error' : 'Info'}</div>
        <div class="toast-message">${message}</div>
    `;
    
    document.body.appendChild(toast);
    
    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Hide toast after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

function initializeTooltips() {
    // Add tooltips for better UX
    const toolCards = document.querySelectorAll('.tool-card');
    
    toolCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
