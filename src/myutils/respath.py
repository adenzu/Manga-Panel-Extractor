import os
import sys

build_paths = dict([(os.path.normpath(x[0]), os.path.normpath(x[1])) for x in [
    ("icon.ico", "icon.ico"),
    ("src/ai-models/2024-11-00/best.pt", "models/best.pt"),
]])

# Function to get the correct path to bundled resources
def resource_path(relative_path: str) -> str:
    relative_path = os.path.normpath(relative_path)
    if hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        return build_paths[relative_path]
    else:
        return relative_path
