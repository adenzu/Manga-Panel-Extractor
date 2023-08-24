import cv2
import numpy as np
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
)
from PyQt5.QtCore import QThread, pyqtSignal
import os
from dataclasses import dataclass


supported_types = [
    ".bmp",
    ".dib",
    ".jpeg",
    ".jpg",
    ".jpe",
    ".jp2",
    ".png",
    ".webp",
    ".pbm",
    ".pgm",
    ".pp",
    ".pxm",
    ".pnm",
    ".pfm",
    ".sr",
    ".ras",
    ".tiff",
    ".tif",
    ".exr",
    ".hdr",
    ".pic",
]


@dataclass
class GrayscaleImage:
    image: np.ndarray
    image_name: str


def get_file_names(directory_path: str) -> list[str]:
    """
    Returns the names of the files in the given directory
    """
    return [
        file_name
        for file_name in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, file_name))
    ]


def load_grayscale_image(directory_path: str, image_name: str) -> GrayscaleImage:
    """
    Returns a GrayscaleImage object from the given image name in the given directory
    """
    image = cv2.imread(os.path.join(
        directory_path, image_name), cv2.IMREAD_GRAYSCALE)
    return GrayscaleImage(image, image_name)


def get_file_extension(file_path: str) -> str:
    """
    Returns the extension of the given file path
    """
    return os.path.splitext(file_path)[1]


def load_grayscale_images(directory_path: str) -> list[GrayscaleImage]:
    """
    Returns a list of GrayscaleImage objects from the images in the given directory
    """
    file_names = get_file_names(directory_path)
    image_names = filter(lambda x: get_file_extension(x)
                         in supported_types, file_names)
    return [
        load_grayscale_image(directory_path, image_name) for image_name in image_names
    ]


def generate_background_mask(image: np.ndarray) -> np.ndarray:
    """
    Generates a mask by focusing on the largest area of white pixels
    """
    WHITE = 255
    LESS_WHITE = 240

    ret, thresh = cv2.threshold(image, LESS_WHITE, WHITE, cv2.THRESH_BINARY)
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        thresh)

    mask = np.zeros_like(thresh)

    max_contour_candidate_count = 30
    guaranteed_top_contour_count = 1

    if max_contour_candidate_count > 1:
        for i in np.argsort(stats[1:, 4])[::-1][:max_contour_candidate_count]:
            x, y, w, h, area = stats[i + 1]
            if guaranteed_top_contour_count > 0 or (
                w * h > area * 0.9 and w * h < area * 1.1
            ):
                mask[labels == i + 1] = WHITE
            guaranteed_top_contour_count -= 1
    else:
        mask[labels == np.argmax(stats[1:, 4]) + 1] = WHITE

    # Apply dilation to expand the white regions
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)

    return mask


def extract_panels(image: np.ndarray, panel_contours: list[np.ndarray]) -> list[np.ndarray]:
def generate_background_mask_with_pointiness_focus(image: np.ndarray, debug: bool = False) -> np.ndarray:
    """
    Generates a mask by focusing on the most pointy white regions
    """
    WHITE = 255
    LESS_WHITE = 240

    ret, thresh = cv2.threshold(image, LESS_WHITE, WHITE, cv2.THRESH_BINARY)
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        thresh)

    mask = np.zeros_like(thresh)
    labeled_objects = np.zeros_like(image)

    max_contour_candidate_count = 30
    guaranteed_top_contour_count = 1

    if max_contour_candidate_count > 1:
        pointiness_ratios = []
        for i in np.argsort(stats[1:, 4])[::-1][:max_contour_candidate_count]:
            label = i + 1
            object_pixels = np.where(labels == label, 255, 0).astype(np.uint8)
            contours, _ = cv2.findContours(
                object_pixels,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_NONE,
            )
            if len(contours) > 0:
                contour = contours[0]
                perimeter = cv2.arcLength(contour, True)
                epsilon = 0.01 * perimeter
                approx = cv2.approxPolyDP(contour, epsilon, True)
                corners = len(approx)

                if perimeter > 0:
                    pointiness_ratio = corners / perimeter
                    pointiness_ratios.append((label, pointiness_ratio))

                    # Debugging: Draw labeled object on the labeled_objects image
                    if debug:
                        cv2.drawContours(labeled_objects, [
                                         contour], 0, generate_random_color(), -1)
                        M = cv2.moments(contour)
                        centroid_x = int(M["m10"] / M["m00"])
                        centroid_y = int(M["m01"] / M["m00"])
                        text = f'Label: {label}, Corner Count: {corners}, Pointiness: {pointiness_ratio:.2f}'
                        text_size, _ = cv2.getTextSize(
                            text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                        text_x = centroid_x - text_size[0] // 2
                        text_y = centroid_y + text_size[1] // 2
                        cv2.putText(labeled_objects, text, (text_x, text_y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1, cv2.LINE_AA)

        sorted_labels = sorted(pointiness_ratios, key=lambda x: x[1])

        for label, pointiness_ratio in sorted_labels:
            x, y, w, h, area = stats[label]
            if guaranteed_top_contour_count > 0 or (
                w * h > area * 0.9 and w * h < area * 1.1
            ):
                mask[labels == label] = WHITE
            guaranteed_top_contour_count -= 1
    else:
        label = np.argmax(stats[1:, 4]) + 1
        mask[labels == label] = WHITE

    # Apply dilation to expand the white regions
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # Debugging: Display the labeled objects image and the final mask
    if debug:
        cv2.imshow('Labeled Objects', labeled_objects)
        cv2.imshow('Final Mask', mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return mask
    """
    Extracts panels from the image using the given contours corresponding to the panels
    """
    PAGE_TO_PANEL_RATIO = 16

    height, width = image.shape
    image_area = width * height
    area_threshold = image_area // PAGE_TO_PANEL_RATIO

    returned_panels = []

    for contour in panel_contours:
        area = cv2.contourArea(contour)

        if area < area_threshold:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        panel = np.zeros_like(image)

        cv2.drawContours(panel, [contour], 0, (255, 255, 255), -1)

        panel = cv2.bitwise_and(image, image, mask=panel)

        fitted_panel = panel[y: y + h, x: x + w]

        returned_panels.append(fitted_panel)
    
    return returned_panels


def generate_panel_blocks(image: np.ndarray) -> list[np.ndarray]:
    mask = generate_background_mask(image)
    """
    Generates the separate panel images from the base image
    """

    result = cv2.subtract(image, mask)

    contours, _ = cv2.findContours(
        result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return extract_panels(image, contours)


def extract_panels_for_image(image_path: str, output_dir: str):
    """
    Extracts panels for a single image
    """
    image = load_grayscale_image(os.path.dirname(image_path), image_path)
    image_name, image_ext = os.path.splitext(image.image_name)
    for k, panel in enumerate(generate_panel_blocks(image.image)):
        out_path = os.path.join(output_dir, f"{image_name}_{k}{image_ext}")
        cv2.imwrite(out_path, panel)


def extract_panels_for_images_in_folder(input_dir: str, output_dir: str):
    """
    Basically the main function of the program,
    this is written with cli usage in mind
    """
    files = os.listdir(input_dir)
    total_files = len(files)
    for i, image in enumerate(tqdm(load_grayscale_images(input_dir), total=total_files)):
        image_name, image_ext = os.path.splitext(image.image_name)
        for k, panel in enumerate(generate_panel_blocks(image.image)):
            out_path = os.path.join(output_dir, f"{image_name}_{k}{image_ext}")
            cv2.imwrite(out_path, panel)


class ExtractionThread(QThread):
    progress_update = pyqtSignal(str)
    process_finished = pyqtSignal()

    def __init__(self, input_dir: str, output_dir: str):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir

    def run(self):
        files = os.listdir(self.input_dir)
        total_files = len(files)
        for i, image in enumerate(load_grayscale_images(self.input_dir)):
            if self.isInterruptionRequested():
                return
            self.progress_update.emit(f"Processing file {i+1}/{total_files}")
            image_name, image_ext = os.path.splitext(image.image_name)
            for k, panel in enumerate(generate_panel_blocks(image.image)):
                out_path = os.path.join(
                    self.output_dir, f"{image_name}_{k}{image_ext}")
                cv2.imwrite(out_path, panel)
        self.process_finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create widgets
        self.label1 = QLabel("Input Directory", self)
        self.textbox1 = QLineEdit(self)
        self.button1 = QPushButton("Browse", self)
        self.label2 = QLabel("Output Directory", self)
        self.textbox2 = QLineEdit(self)
        self.button2 = QPushButton("Browse", self)
        self.button3 = QPushButton("Start", self)
        self.button4 = QPushButton("Cancel", self)

        # Set widget positions and sizes
        self.label1.setGeometry(20, 40, 100, 30)
        self.textbox1.setGeometry(130, 40, 200, 30)
        self.button1.setGeometry(350, 40, 80, 30)

        self.label2.setGeometry(20, 90, 100, 30)
        self.textbox2.setGeometry(130, 90, 200, 30)
        self.button2.setGeometry(350, 90, 80, 30)

        self.button3.setGeometry(200, 140, 80, 30)

        # Connect signals and slots
        self.button1.clicked.connect(self.open_directory_dialog1)
        self.button2.clicked.connect(self.open_directory_dialog2)
        self.button3.clicked.connect(self.start_extracting)
        self.button4.clicked.connect(self.cancel_extraction)

        self.button4.setEnabled(False)

        # Set window properties
        self.setWindowTitle("Manga Panel Extractor")
        self.setMinimumSize(500, 200)

    def open_directory_dialog1(self):
        # Open directory selection dialog
        directory = str(
            QFileDialog.getExistingDirectory(self, "Select Input Directory")
        )

        file_names = get_file_names(directory)
        number_of_images = len(
            list(
                filter(lambda x: os.path.splitext(x)[
                       1] in supported_types, file_names)
            )
        )

        self.update_progress(f"Found {number_of_images} images")

        # Set the text box value to the selected directory
        self.textbox1.setText(directory)

    def open_directory_dialog2(self):
        # Open directory selection dialog
        directory = str(
            QFileDialog.getExistingDirectory(self, "Select Output Directory")
        )

        # Set the text box value to the selected directory
        self.textbox2.setText(directory)

    def resizeEvent(self, event):
        # Resize and center the widgets when the window is resized
        width = event.size().width()
        height = event.size().height()

        self.label1.setGeometry(
            int(width * 0.04), int(height *
                                   0.2), int(width * 0.2), int(height * 0.1)
        )
        self.textbox1.setGeometry(
            int(width * 0.3), int(height *
                                  0.2), int(width * 0.4), int(height * 0.1)
        )
        self.button1.setGeometry(
            int(width * 0.75), int(height *
                                   0.2), int(width * 0.2), int(height * 0.1)
        )

        self.label2.setGeometry(
            int(width * 0.04), int(height *
                                   0.5), int(width * 0.2), int(height * 0.1)
        )
        self.textbox2.setGeometry(
            int(width * 0.3), int(height *
                                  0.5), int(width * 0.4), int(height * 0.1)
        )
        self.button2.setGeometry(
            int(width * 0.75), int(height *
                                   0.5), int(width * 0.2), int(height * 0.1)
        )

        self.button3.setGeometry(
            int(width * 0.35), int(height *
                                   0.8), int(width * 0.1), int(height * 0.1)
        )
        self.button4.setGeometry(
            int(width * 0.55), int(height *
                                   0.8), int(width * 0.1), int(height * 0.1)
        )

    def start_extracting(self):
        input_dir = self.textbox1.text()
        output_dir = self.textbox2.text()

        if input_dir and output_dir:
            self.button1.setEnabled(False)
            self.button2.setEnabled(False)
            self.button3.setEnabled(False)
            self.button4.setEnabled(True)

            # Start extraction thread
            self.extraction_thread = ExtractionThread(input_dir, output_dir)
            self.extraction_thread.progress_update.connect(
                self.update_progress)
            self.extraction_thread.process_finished.connect(
                self.extracting_finished)
            self.extraction_thread.start()

    def update_progress(self, text):
        # Update the progress label
        self.statusBar().showMessage(text)

    def cancel_extraction(self):
        # Cancel the extraction process
        if hasattr(self, "extraction_thread"):
            self.extraction_thread.requestInterruption()
            self.extraction_thread.wait()

        # Reset the progress label and enable buttons
        self.update_progress("")

        self.button1.setEnabled(True)
        self.button2.setEnabled(True)
        self.button3.setEnabled(True)
        self.button4.setEnabled(False)

    def extracting_finished(self):
        self.button1.setEnabled(True)
        self.button2.setEnabled(True)
        self.button3.setEnabled(True)
        self.button4.setEnabled(False)
        self.update_progress("Finished process")
        self.extraction_thread = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
