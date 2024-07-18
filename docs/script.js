let processedImages = [];

function onOpenCvReady() {
    document.getElementById('start-button').addEventListener('click', () => {
        const inputFiles = document.getElementById('input-files').files;
        const fallback = document.getElementById('fallback').checked;
        const splitJointPanels = document.getElementById('split-joint-panels').checked;

        if (inputFiles.length === 0) {
            alert('Please select input files.');
            return;
        }

        processedImages = [];
        document.getElementById('image-grid').innerHTML = '';

        Array.from(inputFiles).forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    processImage(img);
                }
                img.src = e.target.result;
            }
            reader.readAsDataURL(file);
        });

        // Enable download button after processing
        document.getElementById('download-button').disabled = false;
    });

    document.getElementById('download-button').addEventListener('click', () => {
        downloadAllImages();
    });
}

function processImage(image) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = image.width;
    canvas.height = image.height;
    ctx.drawImage(image, 0, 0);

    let src = cv.imread(canvas);
    let gray = new cv.Mat();
    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);
    let blurred = new cv.Mat();
    let ksize = new cv.Size(3, 3);
    cv.GaussianBlur(gray, blurred, ksize, 0, 0, cv.BORDER_DEFAULT);
    let laplacian = new cv.Mat();
    cv.Laplacian(blurred, laplacian, cv.CV_8U, 1, 1, 0, cv.BORDER_DEFAULT);
    let dilated = new cv.Mat();
    let M = cv.Mat.ones(5, 5, cv.CV_8U);
    cv.dilate(laplacian, dilated, M, new cv.Point(-1, -1), 1, cv.BORDER_CONSTANT, cv.morphologyDefaultBorderValue());
    let inverted = new cv.Mat();
    cv.bitwise_not(dilated, inverted);

    cv.imshow(canvas, inverted);

    // Save the processed image
    processedImages.push(canvas.toDataURL('image/png'));

    // Clean up
    src.delete();
    gray.delete();
    blurred.delete();
    laplacian.delete();
    dilated.delete();
    M.delete();
    inverted.delete();

    updateImageGrid();
}

function updateImageGrid() {
    const grid = document.getElementById('image-grid');
    grid.innerHTML = '';

    const maxImages = 10; // Change this number to control how many images are shown
    const imagesToShow = processedImages.slice(0, maxImages);

    imagesToShow.forEach((dataUrl, index) => {
        const img = document.createElement('img');
        img.src = dataUrl;
        img.addEventListener('click', () => showModal(dataUrl));
        grid.appendChild(img);
    });
}

function showModal(imageSrc) {
    const modal = document.getElementById('modal');
    const modalImg = document.getElementById('modal-img');
    const closeModal = document.getElementById('close-modal');

    modal.style.display = 'block';
    modalImg.src = imageSrc;

    closeModal.onclick = () => {
        modal.style.display = 'none';
    }

    modal.onclick = () => {
        modal.style.display = 'none';
    }
}

function downloadAllImages() {
    const zip = new JSZip();
    processedImages.forEach((dataUrl, index) => {
        const imgData = dataUrl.split(',')[1];
        zip.file(`image_${index + 1}.png`, imgData, { base64: true });
    });

    zip.generateAsync({ type: 'blob' }).then(function (content) {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(content);
        link.download = 'manga_panels.zip';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
}
