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
model = torch.hub.load('ultralytics/yolov5', 'custom', path=resource_path('src/ai-models/2024-11-00/best.pt'))
pathlib.PosixPath = temp