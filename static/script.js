// Global state
let images = [];
let draggedElement = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');

    // Upload zone drag and drop
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);

    // File input change
    fileInput.addEventListener('change', function(e) {
        handleFiles(e.target.files);
    });

    // Generate PDF button
    document.getElementById('generatePdfBtn').addEventListener('click', generatePDF);

    // Clear all button
    document.getElementById('clearAllBtn').addEventListener('click', clearAll);
});

// Drag and drop handlers for upload zone
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    handleFiles(files);
}

// Handle file uploads
async function handleFiles(files) {
    const fileArray = Array.from(files);
    const validFiles = fileArray.filter(file => {
        const isImage = file.type.startsWith('image/');
        const isValidSize = file.size <= 16 * 1024 * 1024; // 16MB
        if (!isImage) {
            showToast('⚠️ ' + file.name + ' er ikke et billedfil', 'warning');
        }
        if (!isValidSize) {
            showToast('⚠️ ' + file.name + ' er for stor (max 16MB)', 'warning');
        }
        return isImage && isValidSize;
    });

    if (validFiles.length === 0) return;

    showProgress();

    for (let i = 0; i < validFiles.length; i++) {
        const file = validFiles[i];
        updateProgress((i / validFiles.length) * 100, `Uploader ${i + 1} af ${validFiles.length}...`);

        try {
            await uploadFile(file);
        } catch (error) {
            console.error('Upload fejl:', error);
            showToast('❌ Kunne ikke uploade ' + file.name, 'error');
        }
    }

    hideProgress();
    updateUI();
}

// Upload single file
function uploadFile(file) {
    return new Promise((resolve, reject) => {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                images.push({
                    filename: data.filename,
                    originalName: data.original_name,
                    description: ''
                });
                resolve(data);
            } else {
                reject(data.error);
            }
        })
        .catch(error => reject(error));
    });
}

// Update UI
function updateUI() {
    const imagesSection = document.getElementById('imagesSection');
    const actionsSection = document.getElementById('actionsSection');
    const imagesGrid = document.getElementById('imagesGrid');
    const imageCount = document.getElementById('imageCount');

    if (images.length > 0) {
        imagesSection.style.display = 'block';
        actionsSection.style.display = 'flex';
        imageCount.textContent = images.length;

        // Render images
        imagesGrid.innerHTML = '';
        images.forEach((image, index) => {
            const imageCard = createImageCard(image, index);
            imagesGrid.appendChild(imageCard);
        });
    } else {
        imagesSection.style.display = 'none';
        actionsSection.style.display = 'none';
    }
}

// Create image card
function createImageCard(image, index) {
    const card = document.createElement('div');
    card.className = 'image-card';
    card.draggable = true;
    card.dataset.index = index;

    // Drag events for reordering
    card.addEventListener('dragstart', handleCardDragStart);
    card.addEventListener('dragover', handleCardDragOver);
    card.addEventListener('drop', handleCardDrop);
    card.addEventListener('dragend', handleCardDragEnd);

    const imgUrl = `/static/../uploads/${image.filename}`;

    card.innerHTML = `
        <div class="image-preview" onclick="openModal('${imgUrl}')">
            <img src="${imgUrl}" alt="${image.originalName}">
            <div class="image-overlay">
                <i class="fas fa-search-plus"></i>
            </div>
        </div>
        <div class="image-info">
            <div class="drag-handle">
                <i class="fas fa-grip-vertical"></i>
            </div>
            <div class="image-name" title="${image.originalName}">
                ${image.originalName}
            </div>
            <button class="btn-icon btn-delete" onclick="deleteImage(${index})" title="Slet billede">
                <i class="fas fa-trash"></i>
            </button>
        </div>
        <div class="image-description">
            <textarea
                placeholder="Tilføj en beskrivelse til dette billede..."
                oninput="updateDescription(${index}, this.value)"
                rows="2"
            >${image.description}</textarea>
        </div>
    `;

    return card;
}

// Card drag and drop handlers for reordering
function handleCardDragStart(e) {
    draggedElement = e.currentTarget;
    e.currentTarget.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
}

function handleCardDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';

    const target = e.currentTarget;
    if (draggedElement !== target) {
        target.classList.add('drag-over-card');
    }
    return false;
}

function handleCardDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    e.preventDefault();

    const target = e.currentTarget;
    target.classList.remove('drag-over-card');

    if (draggedElement !== target) {
        const draggedIndex = parseInt(draggedElement.dataset.index);
        const targetIndex = parseInt(target.dataset.index);

        // Reorder array
        const draggedItem = images[draggedIndex];
        images.splice(draggedIndex, 1);
        images.splice(targetIndex, 0, draggedItem);

        updateUI();
        showToast('✓ Billeder omorganiseret', 'success');
    }

    return false;
}

function handleCardDragEnd(e) {
    e.currentTarget.classList.remove('dragging');
    document.querySelectorAll('.image-card').forEach(card => {
        card.classList.remove('drag-over-card');
    });
}

// Update description
function updateDescription(index, value) {
    images[index].description = value;
}

// Delete image
async function deleteImage(index) {
    if (!confirm('Er du sikker på at du vil slette dette billede?')) {
        return;
    }

    const image = images[index];

    try {
        const response = await fetch('/delete-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename: image.filename })
        });

        const data = await response.json();

        if (data.success) {
            images.splice(index, 1);
            updateUI();
            showToast('✓ Billede slettet', 'success');
        } else {
            showToast('❌ Kunne ikke slette billede', 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showToast('❌ Fejl ved sletning', 'error');
    }
}

// Clear all images
async function clearAll() {
    if (!confirm(`Er du sikker på at du vil slette alle ${images.length} billeder?`)) {
        return;
    }

    const deletePromises = images.map(image =>
        fetch('/delete-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename: image.filename })
        })
    );

    try {
        await Promise.all(deletePromises);
        images = [];
        updateUI();
        showToast('✓ Alle billeder slettet', 'success');
    } catch (error) {
        console.error('Clear all error:', error);
        showToast('❌ Fejl ved sletning af billeder', 'error');
    }
}

// Generate PDF
async function generatePDF() {
    if (images.length === 0) {
        showToast('⚠️ Ingen billeder at generere PDF fra', 'warning');
        return;
    }

    const generateBtn = document.getElementById('generatePdfBtn');
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Genererer PDF...';

    try {
        const response = await fetch('/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ images: images })
        });

        const data = await response.json();

        if (data.success) {
            showToast('✓ PDF genereret! Downloader...', 'success');
            // Download the PDF
            window.location.href = data.download_url;
        } else {
            showToast('❌ ' + (data.error || 'Kunne ikke generere PDF'), 'error');
        }
    } catch (error) {
        console.error('Generate PDF error:', error);
        showToast('❌ Fejl ved generering af PDF', 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-file-pdf"></i> Generer PDF';
    }
}

// Progress bar
function showProgress() {
    document.getElementById('progressContainer').style.display = 'block';
}

function hideProgress() {
    document.getElementById('progressContainer').style.display = 'none';
}

function updateProgress(percent, text) {
    document.getElementById('progressFill').style.width = percent + '%';
    document.getElementById('progressText').textContent = text;
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast toast-' + type + ' show';

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Modal for image preview
function openModal(imageSrc) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    modal.style.display = 'flex';
    modalImg.src = imageSrc;
}

function closeModal() {
    document.getElementById('imageModal').style.display = 'none';
}

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('imageModal');
    if (event.target === modal) {
        closeModal();
    }
}

// Close modal on ESC key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});
