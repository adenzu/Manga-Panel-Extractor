import numpy as np
import cv2
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QCheckBox,
)
from PyQt6.QtCore import QThread, pyqtSignal
import os
from dataclasses import dataclass
from typing import Callable
from tqdm import tqdm
import numpy as np
import argparse


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
class ImageWithFilename:
    image: np.ndarray
    image_name: str


def get_file_names(directory_path: str) -> list[str]:
    """
    Returns the names of the files in the given directory
    """
    if not os.path.exists(directory_path):
        return []
    return [
        file_name
        for file_name in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, file_name))
    ]


def load_image(directory_path: str, image_name: str) -> ImageWithFilename:
    """
    Returns a ImageWithFilename object from the given image name in the given directory
    """
    image = cv2.imread(os.path.join(directory_path, image_name))
    return ImageWithFilename(image, image_name)


def get_file_extension(file_path: str) -> str:
    """
    Returns the extension of the given file path
    """
    return os.path.splitext(file_path)[1]


def load_images(directory_path: str) -> list[ImageWithFilename]:
    """
    Returns a list of ImageWithFilename objects from the images in the given directory
    """
    file_names = get_file_names(directory_path)
    image_names = filter(lambda x: get_file_extension(x) in supported_types, file_names)
    return [load_image(directory_path, image_name) for image_name in image_names]


def get_background_intensity_range(grayscale_image: np.ndarray, min_range: int = 1) -> tuple[int, int]:
    """
    Returns the minimum and maximum intensity values of the background of the image
    """
    edges = [grayscale_image[-1, :], grayscale_image[0, :], grayscale_image[:, 0], grayscale_image[:, -1]]
    sorted_edges = sorted(edges, key=lambda x: np.var(x))

    max_intensity = max(sorted_edges[0])
    min_intensity = max(min(min(sorted_edges[0]), max_intensity - min_range), 0)

    return min_intensity, max_intensity


def is_contour_rectangular(contour: np.ndarray) -> bool:
    """
    Returns whether the given contour is rectangular or not
    """
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.01 * perimeter, True)
    return len(approx) == 4


def generate_background_mask(grayscale_image: np.ndarray) -> np.ndarray:
    """
    Generates a mask by focusing on the largest area of white pixels
    """
    WHITE = 255
    LESS_WHITE, _ = get_background_intensity_range(grayscale_image, 25)
    LESS_WHITE = max(LESS_WHITE, 240)

    ret, thresh = cv2.threshold(grayscale_image, LESS_WHITE, WHITE, cv2.THRESH_BINARY)
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        thresh)

    mask = np.zeros_like(thresh)

    PAGE_TO_SEGMENT_RATIO = 1024

    halting_area_size = mask.size // PAGE_TO_SEGMENT_RATIO

    mask_height, mask_width = mask.shape
    base_background_size_error_threshold = 0.05
    whole_background_min_width = mask_width * (1 - base_background_size_error_threshold)
    whole_background_min_height = mask_height * (1 - base_background_size_error_threshold)

    for i in np.argsort(stats[1:, 4])[::-1]:
        x, y, w, h, area = stats[i + 1]
        if area < halting_area_size:
            break
        if (
            (w > whole_background_min_width) or
            (h > whole_background_min_height) or
            (is_contour_rectangular(cv2.findContours((labels == i + 1).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0][0]))
        ):
            mask[labels == i + 1] = WHITE

    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)

    return mask


def extract_panels(
    image: np.ndarray,
    panel_contours: list[np.ndarray],
    accept_page_as_panel: bool = True,
) -> list[np.ndarray]:
    """
    Extracts panels from the image using the given contours corresponding to the panels
    """
    PAGE_TO_PANEL_RATIO = 32

    height, width = image.shape[:2]
    image_area = width * height
    area_threshold = image_area // PAGE_TO_PANEL_RATIO

    returned_panels = []

    for contour in panel_contours:
        x, y, w, h = cv2.boundingRect(contour)

        if not accept_page_as_panel and ((w >= width * 0.99) or (h >= height * 0.99)):
            continue

        area = cv2.contourArea(contour)

        if (area < area_threshold):
            continue

        fitted_panel = image[y: y + h, x: x + w]

        returned_panels.append(fitted_panel)

    return returned_panels


def apply_adaptive_threshold(image: np.ndarray) -> np.ndarray:
    """
    Applies adaptive threshold to the given image
    """
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 0)


def generate_panel_blocks(
        image: np.ndarray, 
        background_generator: Callable[[np.ndarray], np.ndarray] = generate_background_mask,
        split_joint_panels: bool = False,
        fallback: bool = True,
) -> list[np.ndarray]:
    """
    Generates the separate panel images from the base image
    """

    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_image = cv2.GaussianBlur(grayscale_image, (3, 3), 0)
    processed_image = cv2.Laplacian(processed_image, -1)
    processed_image = cv2.dilate(processed_image, np.ones((5, 5), np.uint8), iterations=1)
    processed_image = 255 - processed_image

    mask = background_generator(processed_image)

    STRIPE_FORMAT_MASK_AREA_RATIO = 0.3
    mask_area = np.count_nonzero(mask)
    mask_area_ratio = mask_area / mask.size

    if STRIPE_FORMAT_MASK_AREA_RATIO > mask_area_ratio and split_joint_panels:
        pixels_before = np.count_nonzero(mask)
        mask = cv2.ximgproc.thinning(mask)
        
        up_kernel = np.array([[0, 0, 0], [0, 1, 0], [0, 1, 0]], np.uint8)
        down_kernel = np.array([[0, 1, 0], [0, 1, 0], [0, 0, 0]], np.uint8)
        left_kernel = np.array([[0, 0, 0], [0, 1, 1], [0, 0, 0]], np.uint8)
        right_kernel = np.array([[0, 0, 0], [1, 1, 0], [0, 0, 0]], np.uint8)

        down_right_kernel = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 0]], np.uint8)
        down_left_diagonal_kernel = np.array([[0, 0, 1], [0, 1, 0], [0, 0, 0]], np.uint8)
        up_left_diagonal_kernel = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 1]], np.uint8)
        up_right_diagonal_kernel = np.array([[0, 0, 0], [0, 1, 0], [1, 0, 0]], np.uint8)
        
        PAGE_TO_JOINT_OBJECT_RATIO = 3
        image_height, image_width = grayscale_image.shape

        height_based_size = image_height // PAGE_TO_JOINT_OBJECT_RATIO
        width_based_size = (2 * image_width) // PAGE_TO_JOINT_OBJECT_RATIO

        height_based_size += height_based_size % 2 + 1
        width_based_size += width_based_size % 2 + 1

        up_dilation_kernel = np.zeros((height_based_size, height_based_size), np.uint8)
        up_dilation_kernel[height_based_size // 2:, height_based_size // 2] = 1

        down_dilation_kernel = np.zeros((height_based_size, height_based_size), np.uint8)
        down_dilation_kernel[:height_based_size // 2 + 1, height_based_size // 2] = 1

        left_dilation_kernel = np.zeros((width_based_size, width_based_size), np.uint8)
        left_dilation_kernel[width_based_size // 2, width_based_size // 2:] = 1

        right_dilation_kernel = np.zeros((width_based_size, width_based_size), np.uint8)
        right_dilation_kernel[width_based_size // 2, :width_based_size // 2 + 1] = 1

        min_based_size = min(width_based_size, height_based_size)

        down_right_dilation_kernel = np.identity(min_based_size // 2 + 1, dtype=np.uint8)
        down_right_dilation_kernel = np.pad(down_right_dilation_kernel, ((0, min_based_size // 2), (0, min_based_size // 2)))

        up_left_dilation_kernel = np.identity(min_based_size // 2 + 1, dtype=np.uint8)
        up_left_dilation_kernel = np.pad(up_left_dilation_kernel, ((min_based_size // 2, 0), (0, min_based_size // 2)))

        up_right_dilation_kernel = np.flip(np.identity(min_based_size // 2 + 1, dtype=np.uint8), axis=1)
        up_right_dilation_kernel = np.pad(up_right_dilation_kernel, ((min_based_size // 2, 0), (0, min_based_size // 2)))

        down_left_dilation_kernel = np.flip(np.identity(min_based_size // 2 + 1, dtype=np.uint8), axis=1)
        down_left_dilation_kernel = np.pad(down_left_dilation_kernel, ((0, min_based_size // 2), (min_based_size // 2, 0)))

        match_kernels = [
            up_kernel,
            down_kernel,
            left_kernel,
            right_kernel,
            down_right_kernel,
            down_left_diagonal_kernel,
            up_left_diagonal_kernel,
            up_right_diagonal_kernel,
        ]

        dilation_kernels = [
            up_dilation_kernel,
            down_dilation_kernel,
            left_dilation_kernel,
            right_dilation_kernel,
            down_right_dilation_kernel,
            down_left_dilation_kernel,
            up_left_dilation_kernel,
            up_right_dilation_kernel,
        ]

        def get_dots(grayscale_image: np.ndarray, kernel: np.ndarray) -> tuple[np.ndarray, int]:
            temp = cv2.matchTemplate(grayscale_image, kernel, cv2.TM_CCOEFF_NORMED)
            _, temp = cv2.threshold(temp, 0.9, 1, cv2.THRESH_BINARY)
            temp = np.where(temp == 1, 255, 0).astype(np.uint8)
            pad_height = (kernel.shape[0] - 1) // 2
            pad_width = (kernel.shape[1] - 1) // 2
            temp = cv2.copyMakeBorder(temp, pad_height, kernel.shape[0] - pad_height - 1, pad_width, kernel.shape[1] - pad_width - 1, cv2.BORDER_CONSTANT, value=0)
            return temp
        
        for match_kernel, dilation_kernel in zip(match_kernels, dilation_kernels):
            dots = get_dots(mask, match_kernel)
            lines = cv2.dilate(dots, dilation_kernel, iterations=1)
            mask = cv2.bitwise_or(mask, lines)

        pixels_now = np.count_nonzero(mask)
        dilation_size = pixels_before // (4  * pixels_now)
        dilation_size += dilation_size % 2 + 1
        mask = cv2.dilate(mask, np.ones((dilation_size, dilation_size), np.uint8), iterations=1)

        page_without_background = 255 - mask
    else:
        page_without_background = cv2.subtract(grayscale_image, mask)

    contours, _ = cv2.findContours(page_without_background, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    panels = extract_panels(image, contours)

    if fallback and len(panels) < 2:
        processed_image = cv2.GaussianBlur(grayscale_image, (3, 3), 0)
        processed_image = cv2.Laplacian(processed_image, -1)
        _, thresh = cv2.threshold(processed_image, 8, 255, cv2.THRESH_BINARY)
        processed_image = apply_adaptive_threshold(processed_image)
        processed_image = cv2.subtract(processed_image, thresh)
        processed_image = cv2.dilate(processed_image, np.ones((3, 3), np.uint8), iterations=2)
        contours, _ = cv2.findContours(processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        panels = extract_panels(image, contours, False)

    return panels


def extract_panels_for_image(image_path: str, output_dir: str, fallback: bool = True, split_joint_panels: bool = False):
    """
    Extracts panels for a single image
    """
    if not os.path.exists(image_path):
        return
    image_path = os.path.abspath(image_path)
    image = load_image(os.path.dirname(image_path), image_path)
    image_name, image_ext = os.path.splitext(image.image_name)
    panel_blocks = generate_panel_blocks(image.image, split_joint_panels=split_joint_panels, fallback=fallback)
    for k, panel in enumerate(tqdm(panel_blocks, total=len(panel_blocks))):
        out_path = os.path.join(output_dir, f"{image_name}_{k}{image_ext}")
        cv2.imwrite(out_path, panel)


def extract_panels_for_images_in_folder(input_dir: str, output_dir: str, fallback: bool = True, split_joint_panels: bool = False):
    """
    Basically the main function of the program,
    this is written with cli usage in mind
    """
    if not os.path.exists(output_dir):
        return
    files = os.listdir(input_dir)
    num_files = len(files)
    for i, image in enumerate(tqdm(load_images(input_dir), total=num_files)):
        image_name, image_ext = os.path.splitext(image.image_name)
        for j, panel in enumerate(generate_panel_blocks(image.image, fallback=fallback, split_joint_panels=split_joint_panels)):
            out_path = os.path.join(output_dir, f"{image_name}_{j}{image_ext}")
            cv2.imwrite(out_path, panel)


class ExtractionThread(QThread):
    progress_update = pyqtSignal(str)
    process_finished = pyqtSignal()

    def __init__(self, input_dir: str, output_dir: str, split_joint_panels: bool = False, fallback: bool = True):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.split_joint_panels = split_joint_panels
        self.fallback = fallback

    def run(self):
        files = os.listdir(self.input_dir)
        total_files = len(files)
        for i, image in enumerate(load_images(self.input_dir)):
            if self.isInterruptionRequested():
                return
            self.progress_update.emit(f"Processing file {i+1}/{total_files}")
            image_name, image_ext = os.path.splitext(image.image_name)
            for k, panel in enumerate(generate_panel_blocks(image.image, split_joint_panels=self.split_joint_panels, fallback=self.fallback)):
                out_path = os.path.join(self.output_dir, f"{image_name}_{k}{image_ext}")
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
        self.fallback_checkbox = QCheckBox("Fallback", self)
        self.split_joint_panels_checkbox = QCheckBox("Split Joint Panels", self)

        # Set widget positions and sizes
        self.label1.setGeometry(20, 40, 100, 30)
        self.textbox1.setGeometry(130, 40, 200, 30)
        self.button1.setGeometry(350, 40, 80, 30)

        self.label2.setGeometry(20, 90, 100, 30)
        self.textbox2.setGeometry(130, 90, 200, 30)
        self.button2.setGeometry(350, 90, 80, 30)

        self.button3.setGeometry(200, 140, 80, 30)
        self.button4.setGeometry(300, 140, 80, 30)

        self.fallback_checkbox.setGeometry(250, 160, 80, 30)
        self.split_joint_panels_checkbox.setGeometry(250, 180, 80, 30)

        # Connect signals and slots
        self.button1.clicked.connect(self.open_input_directory_dialog)
        self.button2.clicked.connect(self.open_output_directory_dialog)
        self.button3.clicked.connect(self.start_extracting)
        self.button4.clicked.connect(self.cancel_extraction)

        self.button4.setEnabled(False)

        # Set window properties
        self.setWindowTitle("Manga Panel Extractor")
        self.setMinimumSize(500, 200)

    def open_input_directory_dialog(self):
        # Open directory selection dialog
        directory = str(QFileDialog.getExistingDirectory(self, "Select Input Directory"))

        file_names = get_file_names(directory)
        number_of_images = len(list(filter(lambda x: os.path.splitext(x)[1] in supported_types, file_names)))

        self.update_progress(f"Found {number_of_images} images")

        # Set the text box value to the selected directory
        self.textbox1.setText(directory)

    def open_output_directory_dialog(self):
        # Open directory selection dialog
        directory = str(QFileDialog.getExistingDirectory(self, "Select Output Directory"))

        # Set the text box value to the selected directory
        self.textbox2.setText(directory)

    def resizeEvent(self, event):
        # Resize and center the widgets when the window is resized
        width = event.size().width()
        height = event.size().height()

        self.label1.setGeometry(int(width * 0.04), int(height * 0.2), int(width * 0.2), int(height * 0.1))
        self.textbox1.setGeometry(int(width * 0.3), int(height * 0.2), int(width * 0.4), int(height * 0.1))
        self.button1.setGeometry(int(width * 0.75), int(height * 0.2), int(width * 0.2), int(height * 0.1))

        self.label2.setGeometry(int(width * 0.04), int(height * 0.5), int(width * 0.2), int(height * 0.1))
        self.textbox2.setGeometry(int(width * 0.3), int(height * 0.5), int(width * 0.4), int(height * 0.1))
        self.button2.setGeometry(int(width * 0.75), int(height * 0.5), int(width * 0.2), int(height * 0.1))

        self.button3.setGeometry(int(width * 0.35), int(height * 0.8), int(width * 0.1), int(height * 0.1))
        self.button4.setGeometry(int(width * 0.55), int(height * 0.8), int(width * 0.1), int(height * 0.1))

        self.fallback_checkbox.setGeometry(int(width * 0.3), int(height * 0.6), int(width * 0.4), int(height * 0.1))
        self.split_joint_panels_checkbox.setGeometry(int(width * 0.3), int(height * 0.7), int(width * 0.4), int(height * 0.1))

    def start_extracting(self):
        input_dir = self.textbox1.text()
        output_dir = self.textbox2.text()

        if input_dir and output_dir:
            self.button1.setEnabled(False)
            self.button2.setEnabled(False)
            self.button3.setEnabled(False)
            self.button4.setEnabled(True)

            # Start extraction thread
            self.extraction_thread = ExtractionThread(input_dir, output_dir, self.split_joint_panels_checkbox.isChecked(), self.fallback_checkbox.isChecked())
            self.extraction_thread.progress_update.connect(self.update_progress)
            self.extraction_thread.process_finished.connect(self.extracting_finished)
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


def main():
    parser = argparse.ArgumentParser(description="Extract panels from manga pages")
    
    parser.add_argument("input_dir", type=str, nargs="?", help="Input directory")
    parser.add_argument("output_dir", type=str, nargs="?", help="Output directory")
    parser.add_argument("-s", "--split-joint-panels", action="store_true", help="Split joint panels")
    parser.add_argument("-f", "--fallback", action="store_true", help="Fallback to a more aggressive method if the first one fails")
    parser.add_argument("-g", "--gui", action="store_true", help="Use GUI")
    parser.add_argument("-v", "--version", action="version", version="Manga-Panel-Extractor v1.1.1")

    args = parser.parse_args()

    if len(sys.argv) == 1 or args.gui:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    elif args.input_dir:
        if args.output_dir:
            extract_panels_for_images_in_folder(args.input_dir, args.output_dir, args.fallback, args.split_joint_panels)
        else:
            extract_panels_for_image(args.input_dir, os.path.dirname(args.input_dir), args.fallback, args.split_joint_panels)
    else:
        print("Invalid arguments")
        parser.print_help()
        

if __name__ == "__main__":
    main()