from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt, QThread
from PyQt6 import QtGui
import time
from myutils.respath import resource_path
from gui.splash_screen_ui import Ui_SplashScreen
from image_processing.model import model

class SplashScreen(Ui_SplashScreen):

    def __init__(self, window: QMainWindow) -> None:
        super().__init__()

        self.window = window

        self.setupUi(window)

        self.window.setWindowIcon(QtGui.QIcon(resource_path("icon.ico")))

        self.window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.finished = lambda: None

        self.model_loaded = False
        model.finished = self.__loaded
        model.load()

        self.progress_thread = QThread()
        self.progress_thread.run = self.start
        self.progress_thread.start()

    def __loaded(self):
        self.model_loaded = True

    def start(self):
        total_progress = 100
        simulated_seconds = 10
        simulated_progress = 90
        seconds_per_progress = simulated_seconds / simulated_progress
        for i in range(simulated_progress + 1):
            self.progress(i, total_progress)
            time.sleep(0.01 if self.model_loaded else seconds_per_progress)
        while not self.model_loaded:
            time.sleep(1)
        for i in range(simulated_progress, total_progress + 1):
            self.progress(i)
            time.sleep(0.01)
        # self.finished()

    def progress(self, value: float, max_value: float = 100):
        progress = value / max_value
        ui_value = 1 - progress

        style_sheet = f"""
        QFrame{{
            border-radius: 150px;
            background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{min(ui_value, 0.99)} rgba(85, 85, 255, 0), stop:{min(ui_value + 0.01, 1)} rgba(52, 152, 219, 255));
        }}
        """

        self.circularProgress.setStyleSheet(style_sheet)
        self.loadingPercentage.setText(f"{(100 * progress).__ceil__()}%")
