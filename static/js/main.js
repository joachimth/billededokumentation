// Global state
let uploadedImages = [];
let draggedElement = null;
let draggedIndex = null;

// DOM elements
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadZone = document.getElementById('uploadZone');
const uploadProgress = document.getElementById('uploadProgress');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const imageGallery = document.getElementById('imageGallery');
const gallerySection = document.getElementById('gallerySection');
const imageCount = document.getElementById('imageCount');
const generatePDF = document.getElementById('generatePDF');
const clearAll = document.getElementById('clearAll');
const pdfSection = document.getElementById('pdfSection');
const imageModal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const modalClose = document.querySelector('.modal-close');
const toastContainer = document.getElementById('toastContainer');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateUI();
});

// Event listeners
function initializeEventListeners() {
    // File upload
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);
    uploadZone.addEventListener('click', () => fileInput.click());
    
    // Gallery actions
    generatePDF.addEventListener('click', generatePDFFile);
    clearAll.addEventListener('click', clearAllImages);
    
    // Modal
    modalClose.addEventListener('click', closeModal);
    imageModal.addEventListener('click', function(e) {
        if (e.target === imageModal) closeModal();
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// File handling
function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    processFiles(files);
    fileInput.value = ''; // Reset input
}

function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    uploadZone.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    if (!uploadZone.contains(event.relatedTarget)) {
        uploadZone.classList.remove('dragover');
    }
}

function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    uploadZone.classList.remove('dragover');
    
    const files = Array.from(event.dataTransfer.files);
    processFiles(files);
}

function processFiles(files) {
    const validFiles = files.filter(file => {
        const isValidType = file.type.startsWith('image/');
        const isValidSize = file.size <= 16 * 1024 * 1024; // 16MB
        
        if (!isValidType) {
            showToast('error', `Ugyldig filtype: ${file.name}`);
        }
        if (!isValidSize) {
            showToast('error', `Filen er for stor: ${file.name} (Max 16MB)`);
        }
        
        return isValidType && isValidSize;
    });
    
    if (validFiles.length === 0) {
        showToast('warning', 'Ingen gyldige filer fundet');
        return;
    }
    
    uploadFiles(validFiles);
}

async function uploadFiles(files) {
    showProgress();
    
    try {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                // Create image object
                const imageObj = {
                    id: Date.now() + Math.random(),
                    filename: result.filename,
                    originalName: result.original_name,
                    description: '',
                    file: file
                };
                
                uploadedImages.push(imageObj);
                addImageToGallery(imageObj);
                showToast('success', `Uploadet: ${result.original_name}`);
            } else {
                showToast('error', result.error || `Upload fejlede: ${file.name}`);
            }
            
            // Update progress
            const progress = Math.round(((i + 1) / files.length) * 100);
            updateProgress(progress, `Uploader... (${i + 1}/${files.length})`);
        }
        
        hideProgress();
        updateUI();
        showToast('success', `Uploadet ${files.length} filer succesfuldt`);
        
    } catch (error) {
        hideProgress();
        showToast('error', 'Fejl ved upload: ' + error.message);
    }
}

function showProgress() {
    uploadProgress.style.display = 'block';
    document.body.classList.add('loading');
}

function hideProgress() {
    uploadProgress.style.display = 'none';
    document.body.classList.remove('loading');
}

function updateProgress(percentage, text) {
    progressBar.style.width = percentage + '%';
    progressText.textContent = text || `Upload ${percentage}%`;
}

// Gallery management
function addImageToGallery(imageObj) {
    const imageItem = createImageElement(imageObj);
    imageGallery.appendChild(imageItem);
    updateUI();
}

function createImageElement(imageObj) {
    const imageItem = document.createElement('div');
    imageItem.className = 'image-item';
    imageItem.draggable = true;
    imageItem.dataset.id = imageObj.id;
    
    // Create image URL for preview
    const imageUrl = URL.createObjectURL(imageObj.file);
    
    imageItem.innerHTML = `
        <img src="${imageUrl}" alt="${imageObj.originalName}" class="image-preview" 
             onclick="openModal('${imageUrl}', '${imageObj.originalName}')">
        <div class="image-content">
            <textarea 
                class="image-description" 
                placeholder="Tilføj beskrivelse (valgfrit)"
                data-id="${imageObj.id}">${imageObj.description}</textarea>
            <div class="image-actions">
                <i class="fas fa-grip-vertical move-handle" title="Træk for at omorganisere"></i>
                <button class="delete-btn" onclick="removeImage('${imageObj.id}')" title="Slet billede">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    // Add drag and drop events
    imageItem.addEventListener('dragstart', handleDragStart);
    imageItem.addEventListener('dragover', handleDragOver);
    imageItem.addEventListener('drop', handleDrop);
    imageItem.addEventListener('dragend', handleDragEnd);
    
    // Add description change event
    const descriptionField = imageItem.querySelector('.image-description');
    descriptionField.addEventListener('input', function() {
        const imageId = this.dataset.id;
        const image = uploadedImages.find(img => img.id == imageId);
        if (image) {
            image.description = this.value;
        }
    });
    
    return imageItem;
}

function updateUI() {
    // Update gallery visibility
    if (uploadedImages.length > 0) {
        gallerySection.style.display = 'block';
    } else {
        gallerySection.style.display = 'none';
    }
    
    // Update image count
    const count = uploadedImages.length;
    imageCount.textContent = `${count} billed${count !== 1 ? 'er' : ''}`;
    
    // Update generate PDF button
    generatePDF.disabled = count === 0;
}

function removeImage(id) {
    const index = uploadedImages.findIndex(img => img.id == id);
    if (index !== -1) {
        // Remove from state
        uploadedImages.splice(index, 1);
        
        // Remove from DOM
        const imageElement = document.querySelector(`[data-id="${id}"]`);
        if (imageElement) {
            imageElement.remove();
        }
        
        // Send delete request to server
        fetch('/delete-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: getImageById(id).filename })
        }).catch(error => console.log('Delete request failed:', error));
        
        showToast('success', 'Billede fjernet');
        updateUI();
    }
}

function clearAllImages() {
    if (uploadedImages.length === 0) return;
    
    if (confirm('Er du sikker på, at du vil fjerne alle uploadede billeder?')) {
        uploadedImages.forEach(image => {
            fetch('/delete-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename: image.filename })
            }).catch(error => console.log('Delete request failed:', error));
        });
        
        uploadedImages = [];
        imageGallery.innerHTML = '';
        updateUI();
        showToast('success', 'Alle billeder fjernet');
    }
}

function getImageById(id) {
    return uploadedImages.find(img => img.id == id);
}

// Drag and drop reordering
function handleDragStart(e) {
    draggedElement = e.currentTarget;
    draggedIndex = Array.from(imageGallery.children).indexOf(draggedElement);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', draggedElement.outerHTML);
    draggedElement.classList.add('dragging');
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    
    const afterElement = getDragAfterElement(imageGallery, e.clientY);
    const draggable = document.querySelector('.dragging');
    
    if (!afterElement) {
        imageGallery.appendChild(draggable);
    } else {
        imageGallery.insertBefore(draggable, afterElement);
    }
}

function handleDrop(e) {
    e.preventDefault();
    draggedElement.classList.remove('dragging');
    
    // Update order in state
    const newOrder = Array.from(imageGallery.children).map(child => child.dataset.id);
    uploadedImages.sort((a, b) => newOrder.indexOf(a.id.toString()) - newOrder.indexOf(b.id.toString()));
}

function handleDragEnd(e) {
    draggedElement = null;
    draggedIndex = null;
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.image-item:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// PDF generation
async function generatePDFFile() {
    if (uploadedImages.length === 0) {
        showToast('warning', 'Ingen billeder at generere PDF fra');
        return;
    }
    
    generatePDF.disabled = true;
    generatePDF.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Genererer...';
    pdfSection.style.display = 'block';
    
    try {
        const images = uploadedImages.map(img => ({
            filename: img.filename,
            description: img.description
        }));
        
        const response = await fetch('/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ images })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // Auto download
            const link = document.createElement('a');
            link.href = result.download_url;
            link.download = 'photo_documentation.pdf';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showToast('success', 'PDF genereret og downloadstartet!');
        } else {
            showToast('error', result.error || 'Fejl ved PDF-generering');
        }
        
    } catch (error) {
        showToast('error', 'Fejl ved PDF-generering: ' + error.message);
    } finally {
        generatePDF.disabled = false;
        generatePDF.innerHTML = '<i class="fas fa-file-pdf"></i> Generer PDF';
        pdfSection.style.display = 'none';
    }
}

// Modal functions
function openModal(imageSrc, alt) {
    modalImage.src = imageSrc;
    modalImage.alt = alt || 'Billede';
    imageModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    imageModal.style.display = 'none';
    document.body.style.overflow = '';
    modalImage.src = '';
}

// Toast notifications
function showToast(type, message, duration = 4000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <div class="toast-content">
            <i class="toast-icon ${iconMap[type] || iconMap.info}"></i>
            <span class="toast-message">${message}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after duration
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, duration);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 10);
}

// Keyboard shortcuts
function handleKeyboardShortcuts(e) {
    // ESC to close modal
    if (e.key === 'Escape') {
        closeModal();
    }
    
    // Ctrl/Cmd + Enter to generate PDF
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !generatePDF.disabled) {
        generatePDFFile();
    }
    
    // Delete key to remove selected image
    if (e.key === 'Delete' && e.target.classList.contains('image-description')) {
        // Find the image and remove it
        const imageId = e.target.dataset.id;
        if (imageId) {
            removeImage(imageId);
        }
    }
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getFileExtension(filename) {
    return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2);
}

// Performance monitoring
function logPerformance() {
    if (window.performance && window.performance.timing) {
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log(`Page load time: ${loadTime}ms`);
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showToast('error', 'Der opstod en uventet fejl');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showToast('error', 'En uventet fejl opstod');
});

// Initialize performance monitoring
window.addEventListener('load', logPerformance);

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        handleFileSelect,
        processFiles,
        removeImage,
        clearAllImages,
        showToast
    };
}