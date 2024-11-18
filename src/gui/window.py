import os
from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox, QFileDialog
from myutils.myutils import get_file_names, supported_types
from gui.extractor import ExtractionThread
from gui.base_window import Ui_MainWindow

class MainWindowUI(Ui_MainWindow):
    def __init__(self, window: QMainWindow) -> None:
        super().__init__()

        self.window = window

        self.setupUi(window)

        self.input_directory_browse_button.clicked.connect(self.open_input_directory_dialog)
        self.output_directory_browse_button.clicked.connect(self.open_output_directory_dialog)
        self.start_button.clicked.connect(self.start_extracting)
        self.cancel_button.clicked.connect(self.cancel_extraction)
        
    def open_input_directory_dialog(self):
        # Open directory selection dialog
        directory = str(QFileDialog.getExistingDirectory(self.window, "Select Input Directory"))

        file_names = get_file_names(directory)
        number_of_images = len(list(filter(lambda x: os.path.splitext(x)[1] in supported_types, file_names)))

        self.set_status(f"Found {number_of_images} images")

        # Set the text box value to the selected directory
        self.input_directory_line_edit.setText(directory)

    def open_output_directory_dialog(self):
        # Open directory selection dialog
        directory = str(QFileDialog.getExistingDirectory(self.window, "Select Output Directory"))

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
                self.split_joint_panels_check_box.isChecked(), 
                self.use_fallback_check_box.isChecked(), 
                self.output_separate_folders_check_box.isChecked(),
                self.output_mode_combo_box.currentIndex(),
                self.merge_mode_combo_box.currentIndex()
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
