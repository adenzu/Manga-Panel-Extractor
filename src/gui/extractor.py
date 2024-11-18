import os
import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from myutils.myutils import load_images, ImageWithFilename
from image_processing.panel import generate_panel_blocks, OutputMode, MergeMode

class ExtractionThread(QThread):
    progress_update = pyqtSignal(int, int)
    process_finished = pyqtSignal()

    def __init__(self, 
                input_dir: str, 
                output_dir: str, 
                split_joint_panels: bool = False, 
                fallback: bool = False, 
                output_to_folders: bool = False,
                output_mode: int = 0,
                merge_mode: int = 0
                ):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.split_joint_panels = split_joint_panels
        self.fallback = fallback
        self.output_to_folders = output_to_folders
        self.output_mode = OutputMode.from_index(output_mode)
        self.merge_mode = MergeMode.from_index(merge_mode)

    def run(self):
        files = os.listdir(self.input_dir)
        total_files = len(files)

        def extract(image: ImageWithFilename, output_folder: str):
            image_name, image_ext = os.path.splitext(image.image_name)
            for k, panel in enumerate(
                generate_panel_blocks(
                image.image, 
                split_joint_panels=self.split_joint_panels, 
                fallback=self.fallback, 
                mode=self.output_mode, 
                merge=self.merge_mode
                )
            ):
                    out_path = os.path.join(output_folder, f"{image_name}_{k}{image_ext}")
                    cv2.imwrite(out_path, panel)

        for i, image in enumerate(load_images(self.input_dir)):
            if self.isInterruptionRequested():
                return
            self.progress_update.emit(i + 1, total_files)
            image_name, image_ext = os.path.splitext(image.image_name)
            output_folder = self.output_dir
            if self.output_to_folders:
                output_folder = os.path.join(self.output_dir, image_name)
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
            extract(image, output_folder)
        self.process_finished.emit()