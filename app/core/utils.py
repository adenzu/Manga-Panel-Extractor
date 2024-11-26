import os
from dataclasses import dataclass
import cv2
import numpy as np

supported_types = [
    ".bmp",
    ".dib",
    ".jpeg",
    ".jpg",
    ".jpe",
    ".jp2",
    ".png",
    ".webp",
    ".pbm",
    ".pgm",
    ".pp",
    ".pxm",
    ".pnm",
    ".pfm",
    ".sr",
    ".ras",
    ".tiff",
    ".tif",
    ".exr",
    ".hdr",
    ".pic",
]


@dataclass
class ImageWithFilename:
    image: np.ndarray
    image_name: str


def get_file_extension(file_path: str) -> str:
    """
    Returns the extension of the given file path
    """
    return os.path.splitext(file_path)[1]


def load_image(directory_path: str, image_name: str) -> ImageWithFilename:
    """
    Returns an ImageWithFilename object from the given image name in the given directory
    """
    image = cv2.imread(os.path.join(directory_path, image_name))
    return ImageWithFilename(image, image_name)


def load_images(directory_path: str) -> list[ImageWithFilename]:
    """
    Returns a list of ImageWithFilename objects from the images in the given directory
    """
    file_names = get_file_names(directory_path)
    image_names = filter(lambda x: get_file_extension(x) in supported_types, file_names)
    return [load_image(directory_path, image_name) for image_name in image_names]


def get_file_names(directory_path: str) -> list[str]:
    """
    Returns the names of the files in the given directory
    """
    if not os.path.exists(directory_path):
        return []
    return [
        file_name
        for file_name in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, file_name))
    ]
