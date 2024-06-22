import os
from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox, QFileDialog

# TODO: Clean up the GUI positioning and resizing code
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create widgets
        self.inputDirectoryLabel = QLabel("Input Directory", self)
        self.inputDirectoryTextbox = QLineEdit(self)
        self.selectInputDirectoryButton = QPushButton("Browse", self)
        
        self.outputDirectoryLabel = QLabel("Output Directory", self)
        self.outputDirectoryTextbox = QLineEdit(self)
        self.selectOutputDirectoryButton = QPushButton("Browse", self)

        self.fallbackCheckbox = QCheckBox("Fallback", self)
        self.splitJointPanelsCheckbox = QCheckBox("Split Joint Panels", self)
        self.outputToFoldersCheckbox = QCheckBox("Output to Separate Folders", self)
        
        self.startButton = QPushButton("Start", self)
        self.cancelButton = QPushButton("Cancel", self)

        self.questionMarkButton = QPushButton("?", self)

        # Set widget positions and sizes
        self.inputDirectoryLabel.setGeometry(20, 20, 100, 20)
        self.inputDirectoryTextbox.setGeometry(150, 20, 200, 20)
        self.selectInputDirectoryButton.setGeometry(375, 20, 100, 20)

        self.outputDirectoryLabel.setGeometry(20, 80, 100, 20)
        self.outputDirectoryTextbox.setGeometry(150, 80, 200, 20)
        self.selectOutputDirectoryButton.setGeometry(375, 80, 100, 20)

        self.fallbackCheckbox.setGeometry(150, 100, 200, 20)
        self.splitJointPanelsCheckbox.setGeometry(150, 120, 200, 20)
        self.outputToFoldersCheckbox.setGeometry(150, 140, 200, 20)

        self.startButton.setGeometry(175, 160, 50, 20)
        self.cancelButton.setGeometry(275, 160, 50, 20)

        self.questionMarkButton.setGeometry(20, 160, 20, 20)

        # Set initial values
        self.cancelButton.setEnabled(False)

        # Set checkable properties
        self.questionMarkButton.setCheckable(True)

        # Connect signals and slots
        self.selectInputDirectoryButton.clicked.connect(self.open_input_directory_dialog)
        self.selectOutputDirectoryButton.clicked.connect(self.open_output_directory_dialog)
        self.startButton.clicked.connect(self.start_extracting)
        self.cancelButton.clicked.connect(self.cancel_extraction)
        self.questionMarkButton.clicked.connect(self.show_explanations)

        # Set window properties
        self.setWindowTitle("Manga Panel Extractor")
        self.setMinimumSize(500, 200)

        # List to store widget explanations
        self.explanations = [
            "Input Directory: The directory containing the images to extract panels from",
            "Output Directory: The directory to save the extracted panels to",
            "Browse Buttons: Click to select corresponding directories",
            "Fallback Checkbox: Use a more aggressive method if the base method for panel extraction fails",
            "Split Joint Panels Checkbox: Split joint panels into separate panels",
            "Output to Separate Folders Checkbox: Save extracted panels to separate folders in the main output folder that are named after the input images instead of saving them directly to the main output folder",
            "Start Button: Start the panel extraction process",
            "Cancel Button: Cancel the panel extraction process",
        ]

        # Track currently explained widget
        self.current_explanation_widget = None

    def show_explanations(self):
        explanation_text = "\n\n".join(self.explanations)
        QMessageBox.information(self, "Widget Explanations", explanation_text)

    def open_input_directory_dialog(self):
        # Open directory selection dialog
        directory = str(QFileDialog.getExistingDirectory(self, "Select Input Directory"))

        file_names = get_file_names(directory)
        number_of_images = len(list(filter(lambda x: os.path.splitext(x)[1] in supported_types, file_names)))

        self.update_progress(f"Found {number_of_images} images")

        # Set the text box value to the selected directory
        self.inputDirectoryTextbox.setText(directory)

    def open_output_directory_dialog(self):
        # Open directory selection dialog
        directory = str(QFileDialog.getExistingDirectory(self, "Select Output Directory"))

        # Set the text box value to the selected directory
        self.outputDirectoryTextbox.setText(directory)

    def resizeEvent(self, event):
        # Resize and center the widgets when the window is resized
        width = event.size().width()
        height = event.size().height()

        self.inputDirectoryLabel.setGeometry(int(width * 0.04), int(height * 0.1), int(width * 0.2), int(height * 0.1))
        self.inputDirectoryTextbox.setGeometry(int(width * 0.3), int(height * 0.1), int(width * 0.4), int(height * 0.1))
        self.selectInputDirectoryButton.setGeometry(int(width * 0.75), int(height * 0.1), int(width * 0.2), int(height * 0.1))

        self.outputDirectoryLabel.setGeometry(int(width * 0.04), int(height * 0.4), int(width * 0.2), int(height * 0.1))
        self.outputDirectoryTextbox.setGeometry(int(width * 0.3), int(height * 0.4), int(width * 0.4), int(height * 0.1))
        self.selectOutputDirectoryButton.setGeometry(int(width * 0.75), int(height * 0.4), int(width * 0.2), int(height * 0.1))

        self.fallbackCheckbox.setGeometry(int(width * 0.3), int(height * 0.5), int(width * 0.4), int(height * 0.1))
        self.splitJointPanelsCheckbox.setGeometry(int(width * 0.3), int(height * 0.6), int(width * 0.4), int(height * 0.1))
        self.outputToFoldersCheckbox.setGeometry(int(width * 0.3), int(height * 0.7), int(width * 0.4), int(height * 0.1))

        self.startButton.setGeometry(int(width * 0.35), int(height * 0.8), int(width * 0.1), int(height * 0.1))
        self.cancelButton.setGeometry(int(width * 0.55), int(height * 0.8), int(width * 0.1), int(height * 0.1))

        self.questionMarkButton.setGeometry(int(width * 0.9), int(height * 0.8), int(width * 0.05), int(height * 0.1))
        
    def start_extracting(self):
        input_dir = self.inputDirectoryTextbox.text()
        output_dir = self.outputDirectoryTextbox.text()

        if input_dir and output_dir:
            self.selectInputDirectoryButton.setEnabled(False)
            self.selectOutputDirectoryButton.setEnabled(False)
            self.startButton.setEnabled(False)
            self.cancelButton.setEnabled(True)

            # Start extraction thread
            self.extraction_thread = ExtractionThread(
                input_dir, 
                output_dir, 
                self.splitJointPanelsCheckbox.isChecked(), 
                self.fallbackCheckbox.isChecked(), 
                self.outputToFoldersCheckbox.isChecked()
            )

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

        self.selectInputDirectoryButton.setEnabled(True)
        self.selectOutputDirectoryButton.setEnabled(True)
        self.startButton.setEnabled(True)
        self.cancelButton.setEnabled(False)

    def extracting_finished(self):
        self.selectInputDirectoryButton.setEnabled(True)
        self.selectOutputDirectoryButton.setEnabled(True)
        self.startButton.setEnabled(True)
        self.cancelButton.setEnabled(False)
        self.update_progress("Finished process")
        self.extraction_thread = None
