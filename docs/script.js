document.getElementById('start-button').addEventListener('click', () => {
    const inputFiles = document.getElementById('input-files').files;
    const fallback = document.getElementById('fallback').checked;
    const splitJointPanels = document.getElementById('split-joint-panels').checked;

    if (inputFiles.length === 0) {
        alert('Please select input files.');
        return;
    }

    // Process files and create a zip (dummy process for demonstration)
    setTimeout(() => {
        // Enable download button after processing
        document.getElementById('download-button').disabled = false;
    }, 2000);
});

document.getElementById('download-button').addEventListener('click', () => {
    // Trigger file download (dummy process for demonstration)
    const link = document.createElement('a');
    link.href = 'path/to/your/zipfile.zip'; // Replace with actual zip file path
    link.download = 'manga_panels.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});
