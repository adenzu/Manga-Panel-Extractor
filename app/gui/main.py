import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication, QMainWindow
from app.gui.views.main_window import MainWindowUI
from core.panel import extract_panels_for_image, extract_panels_for_images_in_folder


def start_gui():
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = MainWindowUI(window)
    window.show()
    sys.exit(app.exec())


def make_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser
    """
    parser = argparse.ArgumentParser(description="Extract panels from manga pages")
    
    parser.add_argument("input_dir", type=str, nargs="?", help="Input directory")
    parser.add_argument("output_dir", type=str, nargs="?", help="Output directory")
    parser.add_argument("-s", "--split-joint-panels", action="store_true", help="Split joint panels")
    parser.add_argument("-f", "--fallback", action="store_true", help="Fallback to a more aggressive method if the first one fails")
    parser.add_argument("-g", "--gui", action="store_true", help="Use GUI")
    parser.add_argument("-v", "--version", action="version", version="Manga-Panel-Extractor v1.1.1")
    
    return parser


def handle_parameters() -> None:
    """
    Handle the parameters passed to the program
    """
    parser = make_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1 or args.gui:
        start_gui()
    elif args.input_dir:
        if args.output_dir:
            extract_panels_for_images_in_folder(args.input_dir, args.output_dir, args.fallback, args.split_joint_panels)
        else:
            extract_panels_for_image(args.input_dir, os.path.dirname(args.input_dir), args.fallback, args.split_joint_panels)
    else:
        print("Invalid arguments")
        parser.print_help()


def main():
    handle_parameters()        


if __name__ == "__main__":
    main()