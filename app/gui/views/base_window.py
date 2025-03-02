import os
import cv2
from PyQt6 import QtGui
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QFileDialog
from app.core.panel import OutputMode, MergeMode, generate_panel_blocks_by_ai
from app.core.utils import (
    ImageWithFilename,
    resource_path,
    load_image,
    get_file_names,
    supported_types,
)
from app.gui.resources.ui.main_window_ui import Ui_MainWindow


class ExtractionThread(QThread):
    progress_update = pyqtSignal(int, int)
    process_finished = pyqtSignal()

    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        split_joint_panels: bool = False,
        fallback: bool = False,
        output_to_folders: bool = False,
        output_mode: int = 0,
        merge_mode: int = 0,
    ):
        super().__init__()
        self.input_dir = os.path.normpath(input_dir)
        self.output_dir = os.path.normpath(output_dir)
        self.split_joint_panels = split_joint_panels
        self.fallback = fallback
        self.output_to_folders = output_to_folders
        self.output_mode = OutputMode.from_index(output_mode)
        self.merge_mode = MergeMode.from_index(merge_mode)

    def run(self):
        files = os.listdir(self.input_dir)
        files = list(filter(lambda x: os.path.splitext(x)[1] in supported_types, files))

        total_files = len(files)

        def extract(image: ImageWithFilename, output_folder: str):
            image_name, image_ext = os.path.splitext(image.image_name)
            for k, panel in enumerate(
                generate_panel_blocks_by_ai(image.image, merge=self.merge_mode)
            ):
                out_path = os.path.join(output_folder, f"{image_name}_{k}{image_ext}")
                cv2.imwrite(out_path, panel)

        for i, file in enumerate(files):
            if self.isInterruptionRequested():
                return
            image_name, image_ext = os.path.splitext(file)
            output_folder = self.output_dir
            if self.output_to_folders:
                output_folder = os.path.join(self.output_dir, image_name)
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
            image = load_image(self.input_dir, file)
            extract(image, output_folder)
            self.progress_update.emit(i + 1, total_files)

        self.process_finished.emit()


class MainWindowUI(Ui_MainWindow):
    def __init__(self, window: QMainWindow) -> None:
        super().__init__()

        self.window = window

        self.setupUi(window)

        self.input_directory_browse_button.clicked.connect(
            self.open_input_directory_dialog
        )
        self.output_directory_browse_button.clicked.connect(
            self.open_output_directory_dialog
        )
        self.start_button.clicked.connect(self.start_extracting)
        self.cancel_button.clicked.connect(self.cancel_extraction)

        self.window.setWindowIcon(QtGui.QIcon(resource_path("icon.ico")))

    def open_input_directory_dialog(self):
        # Open directory selection dialog
        directory = str(
            QFileDialog.getExistingDirectory(self.window, "Select Input Directory")
        )

        file_names = get_file_names(directory)
        number_of_images = len(
            list(
                filter(lambda x: os.path.splitext(x)[1] in supported_types, file_names)
            )
        )

        self.set_status(f"Found {number_of_images} images")

        # Set the text box value to the selected directory
        self.input_directory_line_edit.setText(directory)

    def open_output_directory_dialog(self):
        # Open directory selection dialog
        directory = str(
            QFileDialog.getExistingDirectory(self.window, "Select Output Directory")
        )

        # Set the text box value to the selected directory
        self.output_directory_line_edit.setText(directory)

    def update_progress(self, finished: int, total: int):
        # Update the progress label
        self.set_status(f"Processing {finished}/{total}")
        self.progress_bar.setValue(int((finished / total) * 100))

    def set_status(self, message: str):
        self.window.statusBar().showMessage(message)

    def start_extracting(self):
        input_dir = self.input_directory_line_edit.text()
        output_dir = self.output_directory_line_edit.text()

        if input_dir and output_dir:
            self.input_directory_browse_button.setEnabled(False)
            self.output_directory_browse_button.setEnabled(False)
            self.start_button.setEnabled(False)
            self.cancel_button.setEnabled(True)

            # Start extraction thread
            self.extraction_thread = ExtractionThread(
                input_dir,
                output_dir,
                output_to_folders=self.output_separate_folders_check_box.isChecked(),
                merge_mode=self.merge_mode_combo_box.currentIndex(),
            )

            self.extraction_thread.progress_update.connect(self.update_progress)
            self.extraction_thread.process_finished.connect(self.extracting_finished)
            self.extraction_thread.start()

    def cancel_extraction(self):
        # Cancel the extraction process
        if hasattr(self, "extraction_thread"):
            self.extraction_thread.requestInterruption()
            self.extraction_thread.wait()

        # Reset the progress label and enable buttons
        self.set_status("Cancelled")

        self.input_directory_browse_button.setEnabled(True)
        self.output_directory_browse_button.setEnabled(True)
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)

    def extracting_finished(self):
        self.input_directory_browse_button.setEnabled(True)
        self.output_directory_browse_button.setEnabled(True)
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(100)
        self.set_status("Finished process")
        self.extraction_thread = None


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = MainWindowUI(self)
