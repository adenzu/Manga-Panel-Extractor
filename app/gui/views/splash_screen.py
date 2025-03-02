from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QMainWindow
from app.core.model import model
from app.core.utils import resource_path
from app.gui.resources.ui.splash_screen_ui import Ui_SplashScreen


class ProgressWorker(QThread):
    progress_update = pyqtSignal(int)  # Signal to update progress
    model_loaded_signal = pyqtSignal()  # Signal when model is loaded
    completed = pyqtSignal()  # Signal when the task is done

    def __init__(self, model_loaded_flag):
        super().__init__()
        self.model_loaded = model_loaded_flag

    def run(self):
        total_progress = 100
        simulated_waits = [(5, 25), (10, 25), (20, 25), (40, 10), (120, 5)]
        total_simulated_progress = sum([wait[1] for wait in simulated_waits])
        simulated_progress = 0
        for seconds, progress in simulated_waits:
            mseconds_to_wait = int(1000 * seconds / progress)
            for i in range(simulated_progress, simulated_progress + progress):
                self.progress_update.emit(i)  # Emit progress
                self.msleep(10 if self.model_loaded else mseconds_to_wait)
            simulated_progress += progress
        while not self.model_loaded:
            self.sleep(1)
        for i in range(total_simulated_progress, total_progress + 1):
            self.progress_update.emit(i)
            self.msleep(10)
        self.completed.emit()  # Notify completion


class ModelLoader(QThread):
    completed = pyqtSignal()

    def run(self):
        model.load()  # Run model loading in this thread
        self.completed.emit()  # Notify completion


class SplashScreenUI(Ui_SplashScreen):
    def __init__(self, window: QMainWindow) -> None:
        super().__init__()
        self.window = window
        self.setupUi(window)
        self.window.setWindowIcon(QtGui.QIcon(resource_path("icon.ico")))
        self.window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.model_loaded = False

        # Model loading thread
        self.model_loader = ModelLoader()
        self.model_loader.completed.connect(self.__loaded)
        self.model_loader.start()

        # Initialize progress worker
        self.progress_worker = ProgressWorker(self.model_loaded)
        self.progress_worker.progress_update.connect(
            lambda value: self.update_progress(value)
        )
        self.progress_worker.completed.connect(self.window.close)
        self.progress_worker.start()

    def __loaded(self):
        self.model_loaded = True
        self.progress_worker.model_loaded = True

    def update_progress(self, value: int):
        total_progress = 100
        progress = value / total_progress
        ui_value = 1 - progress

        style_sheet = f"""
        QFrame{{
            border-radius: 150px;
            background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{min(ui_value, 0.99)} rgba(85, 85, 255, 0), stop:{min(ui_value + 0.01, 1)} rgba(52, 152, 219, 255));
        }}
        """
        self.circularProgress.setStyleSheet(style_sheet)
        self.loadingPercentage.setText(f"{(100 * progress).__ceil__()}%")


class SplashScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = SplashScreenUI(self)
