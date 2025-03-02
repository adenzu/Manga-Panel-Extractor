import sys
from PyQt6.QtWidgets import QApplication
from app.gui.views.base_window import MainWindow
from app.gui.views.splash_screen import SplashScreen


def start_main_window():
    main_window = MainWindow()
    main_window.show()


def start_splash_screen():
    splash_screen = SplashScreen()
    splash_screen.show()
    splash_screen.closeEvent = lambda _: start_main_window()


def start_gui():
    app = QApplication(sys.argv)
    start_splash_screen()
    sys.exit(app.exec())


def main():
    start_gui()


if __name__ == "__main__":
    main()
