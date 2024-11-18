import torch
import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

model = torch.hub.load('ultralytics/yolov5', 'custom', path='src/ai-models/2024-11-00/best.pt')

pathlib.PosixPath = temp