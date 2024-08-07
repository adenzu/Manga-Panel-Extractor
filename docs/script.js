let numProcessed = 0;
let processedImages = {};
let cancel = false;

const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
const maxImages = isMobile ? 2 : 10; // TODO: Implement a better way to handle this

let thumbnails = [];

function zeroPad(num, places) {
    return String(num).padStart(places, '0');
}

function zeroPadTwo(num) {
    return zeroPad(num, 2);
}

function addProcessedImage(filename, dataUrl) {
    numProcessed++;
    processedImages[filename].push(dataUrl);
    if (thumbnails.length < maxImages) {
        thumbnails.push({ filename: filename, dataUrl: dataUrl });
    }
}

function onOpenCvReady() {
    document.getElementById('download-button').disabled = true;
    document.getElementById('cancel-button').disabled = true;

    document.getElementById('download-button').addEventListener('click', () => {
        downloadAllImages();
    });

    document.getElementById('cancel-button').addEventListener('click', () => {
        cancel = true;
        document.getElementById('cancel-button').disabled = true;
    });

    document.getElementById('start-button').addEventListener('click', () => {
        cancel = false;
        document.getElementById('cancel-button').disabled = false;

        const inputFiles = document.getElementById('input-files').files;
        // const fallback = document.getElementById('fallback').checked;
        // const splitJointPanels = document.getElementById('split-joint-panels').checked;

        if (inputFiles.length === 0) {
            alert('Please select input manga page files.');
            return;
        }

        numProcessed = 0;
        processedImages = {};
        thumbnails = [];
        document.getElementById('image-grid').innerHTML = '';
        document.getElementById('download-button').disabled = true;
        document.getElementById('download-button').textContent = 'Processing Images...';

        let totalFiles = inputFiles.length;
        let processedFiles = 0;
        Array.from(inputFiles).forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    if (!cancel) {
                        processImage(img, file.name.split('.')[0]);
                    }
                    processedFiles++;
                    if (processedFiles === totalFiles) {
                        document.getElementById('download-button').disabled = false;
                        document.getElementById('download-button').textContent = 'Download';
                        document.getElementById('cancel-button').disabled = true;
                    }
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        });
    });
}

function get_background_intensity_range(grayscale_image, threshold) {
    // Dummy implementation
    return 240;
}

function is_contour_rectangular(contour) {
    // Dummy implementation
    return true;
}

function generate_background_mask(grayscale_image) {
    const WHITE = 255;
    let LESS_WHITE = get_background_intensity_range(grayscale_image, 25);
    LESS_WHITE = Math.max(LESS_WHITE, 240);

    let thresh = new cv.Mat();
    cv.threshold(grayscale_image, thresh, LESS_WHITE, WHITE, cv.THRESH_BINARY);

    let labels = new cv.Mat();
    let stats = new cv.Mat();
    let centroids = new cv.Mat();
    let nlabels = cv.connectedComponentsWithStats(thresh, labels, stats, centroids, 4, cv.CV_32S);

    let mask = new cv.Mat.zeros(thresh.rows, thresh.cols, cv.CV_8U);

    const PAGE_TO_SEGMENT_RATIO = 1024;
    const halting_area_size = mask.rows * mask.cols / PAGE_TO_SEGMENT_RATIO;

    const mask_height = mask.rows;
    const mask_width = mask.cols;
    const base_background_size_error_threshold = 0.05;
    const whole_background_min_width = mask_width * (1 - base_background_size_error_threshold);
    const whole_background_min_height = mask_height * (1 - base_background_size_error_threshold);

    let statsArray = stats.data32S;
    let areas = [];
    for (let i = 1; i < nlabels; i++) {
        let area = statsArray[i * stats.cols + cv.CC_STAT_AREA];
        areas.push({ index: i, area: area });
    }

    areas.sort((a, b) => b.area - a.area);

    for (let i = 0; i < areas.length; i++) {
        let label = areas[i].index;
        let area = areas[i].area;
        if (area < halting_area_size) break;

        let x = statsArray[label * stats.cols + cv.CC_STAT_LEFT];
        let y = statsArray[label * stats.cols + cv.CC_STAT_TOP];
        let w = statsArray[label * stats.cols + cv.CC_STAT_WIDTH];
        let h = statsArray[label * stats.cols + cv.CC_STAT_HEIGHT];

        if (w > whole_background_min_width || h > whole_background_min_height) {
            let lowerBound = new cv.Mat(labels.rows, labels.cols, cv.CV_32S, new cv.Scalar(label));
            let upperBound = new cv.Mat(labels.rows, labels.cols, cv.CV_32S, new cv.Scalar(label));
            let labelMask = new cv.Mat();
            cv.inRange(labels, lowerBound, upperBound, labelMask);

            let contours = new cv.MatVector();
            let hierarchy = new cv.Mat();
            cv.findContours(labelMask, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);

            if (contours.size() > 0 && is_contour_rectangular(contours.get(0))) {
                cv.bitwise_or(mask, labelMask, mask);
            }

            lowerBound.delete();
            upperBound.delete();
            labelMask.delete();
            contours.delete();
            hierarchy.delete();
        }
    }

    let kernel = cv.Mat.ones(3, 3, cv.CV_8U);
    cv.dilate(mask, mask, kernel, new cv.Point(-1, -1), 2, cv.BORDER_CONSTANT, cv.morphologyDefaultBorderValue());

    kernel.delete();
    thresh.delete();
    labels.delete();
    stats.delete();
    centroids.delete();

    return mask;
}

function extract_panels(image, panel_contours, accept_page_as_panel = true) {
    const PAGE_TO_PANEL_RATIO = 32;

    const height = image.rows;
    const width = image.cols;
    const image_area = width * height;
    const area_threshold = image_area / PAGE_TO_PANEL_RATIO;

    let returned_panels = [];

    for (let i = 0; i < panel_contours.size(); i++) {
        let contour = panel_contours.get(i);
        let rect = cv.boundingRect(contour);

        if (!accept_page_as_panel && (rect.width >= width * 0.99 || rect.height >= height * 0.99)) {
            continue;
        }

        let area = cv.contourArea(contour);
        if (area < area_threshold) {
            continue;
        }

        let fitted_panel = image.roi(rect);
        returned_panels.push(fitted_panel);
    }

    return returned_panels;
}

function preprocess(gray) {
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

    blurred.delete();
    laplacian.delete();
    dilated.delete();
    M.delete();

    return inverted;
}

function processImage(image, filename) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = image.width;
    canvas.height = image.height;
    ctx.drawImage(image, 0, 0);

    let src = cv.imread(canvas);

    let gray = new cv.Mat();
    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);

    let inverted = preprocess(gray);
    let mask = generate_background_mask(inverted);

    let page_without_background = new cv.Mat();
    cv.subtract(gray, mask, page_without_background);

    let contours = new cv.MatVector();
    let hierarchy = new cv.Mat();
    cv.findContours(page_without_background, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);

    let panels = extract_panels(src, contours);

    processedImages[filename] = [];
    for (let i = 0; i < panels.length; i++) {
        let panelCanvas = document.createElement('canvas');
        cv.imshow(panelCanvas, panels[i]);
        addProcessedImage(filename, panelCanvas.toDataURL('image/png'));
    }

    src.delete();
    gray.delete();
    inverted.delete();
    mask.delete();
    page_without_background.delete();
    contours.delete();
    hierarchy.delete();

    updateImageGrid();
}

function updateImageGrid() {
    const grid = document.getElementById('image-grid');
    grid.innerHTML = '';

    const remainingImages = numProcessed - maxImages;

    thumbnails.forEach((image, index) => {
        const img = document.createElement('img');
        img.src = image.dataUrl;
        img.alt = image.filename;
        img.addEventListener('click', () => showModal(image.dataUrl));
        grid.appendChild(img);
    });

    if (remainingImages > 0) {
        const moreImages = document.createElement('div');
        moreImages.className = 'more-images';
        moreImages.textContent = `+${remainingImages} more`;
        grid.appendChild(moreImages);
    }
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

async function downloadAllImages() {
    const writer = new zip.ZipWriter(new zip.BlobWriter("application/zip"));

    document.getElementById('download-button').disabled = true;

    let total = 0;
    for (var filename in processedImages) {
        for (let i = 0; i < processedImages[filename].length; i++) {
            const image = processedImages[filename][i];
            const imgData = image.split(',')[1];
            const blob = await fetch(`data:image/png;base64,${imgData}`).then(res => res.blob());

            await writer.add(`${filename}_panel_${zeroPadTwo(i + 1)}.png`, new zip.BlobReader(blob));

            document.getElementById('download-button').textContent = `Downloading... (${total + 1}/${numProcessed})`;
            total++;
        }
    }

    const zipBlob = await writer.close();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(zipBlob);
    link.download = 'manga_panels.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    document.getElementById('download-button').textContent = 'Download';
    document.getElementById('download-button').disabled = false;
}