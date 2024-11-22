from PyQt6.QtCore import QThread, pyqtSignal

class Model:
    def __init__(self):
        self.model = None
        self.imported = False
        self.finished = lambda: None
    
    def load(self):
        if self.model is None:
            self.thread = QThread()
            self.thread.run = self.__load
            self.thread.finished.connect(self.finished)
            self.thread.start()

    def __load(self):
        if not self.imported:
            self.imported = True
            import torch
            import pathlib
            import sys
            import os
            from myutils.respath import resource_path

        # Redirect sys.stderr to a file or a valid stream
        if sys.stderr is None:
            sys.stderr = open(os.devnull, 'w')

        temp = pathlib.PosixPath
        pathlib.PosixPath = pathlib.WindowsPath
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=resource_path('src/ai-models/2024-11-00/best.pt'))
        pathlib.PosixPath = temp
    
    def __call__(self, *args, **kwds):
        if self.model is None:
            self.__load()
        return self.model(*args, **kwds)

model = Model()
