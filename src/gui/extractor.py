import os
import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from utils.utils import load_images
from image_processing.panel import generate_panel_blocks

class ExtractionThread(QThread):
    progress_update = pyqtSignal(str)
    process_finished = pyqtSignal()

    def __init__(self, input_dir: str, output_dir: str, split_joint_panels: bool = False, fallback: bool = False, output_to_folders: bool = False):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.split_joint_panels = split_joint_panels
        self.fallback = fallback
        self.output_to_folders = output_to_folders

    def run(self):
        files = os.listdir(self.input_dir)
        total_files = len(files)
        for i, image in enumerate(load_images(self.input_dir)):
            if self.isInterruptionRequested():
                return
            self.progress_update.emit(f"Processing file {i+1}/{total_files}")
            image_name, image_ext = os.path.splitext(image.image_name)
            if self.output_to_folders:
                output_folder = os.path.join(self.output_dir, image_name)
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                for k, panel in enumerate(generate_panel_blocks(image.image, split_joint_panels=self.split_joint_panels, fallback=self.fallback)):
                    out_path = os.path.join(output_folder, f"{image_name}_{k}{image_ext}")
                    cv2.imwrite(out_path, panel)
            else:
                for k, panel in enumerate(generate_panel_blocks(image.image, split_joint_panels=self.split_joint_panels, fallback=self.fallback)):
                    out_path = os.path.join(self.output_dir, f"{image_name}_{k}{image_ext}")
                    cv2.imwrite(out_path, panel)
        self.process_finished.emit()
