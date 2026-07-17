document.addEventListener('DOMContentLoaded', function () {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('resume');
    const browseBtn = document.getElementById('browse-btn');
    const fileNameDisplay = document.getElementById('file-name-display');
    const uploadForm = document.getElementById('upload-form');
    const analyzeBtn = document.getElementById('analyze-btn');

    if (!uploadZone || !fileInput) return;

    const showFileName = (file) => {
        if (file) {
            fileNameDisplay.textContent = `Selected: ${file.name}`;
        }
    };

    browseBtn.addEventListener('click', () => fileInput.click());
    uploadZone.addEventListener('click', (e) => {
        if (e.target !== browseBtn) fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) showFileName(fileInput.files[0]);
    });

    ['dragenter', 'dragover'].forEach((evt) => {
        uploadZone.addEventListener(evt, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach((evt) => {
        uploadZone.addEventListener(evt, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.remove('dragover');
        });
    });

    uploadZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        if (dt && dt.files.length) {
            fileInput.files = dt.files;
            showFileName(dt.files[0]);
        }
    });

    if (uploadForm) {
        uploadForm.addEventListener('submit', () => {
            if (fileInput.files.length) {
                analyzeBtn.disabled = true;
                analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Analyzing...';
            }
        });
    }
});
