import cv2
import numpy as np


def apply_adaptive_threshold(image: np.ndarray) -> np.ndarray:
    """
    Applies adaptive threshold to the given image
    """
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 0)


def is_contour_rectangular(contour: np.ndarray) -> bool:
    """
    Returns whether the given contour is rectangular or not
    """
    num_sides = 4
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.01 * perimeter, True)
    return len(approx) == num_sides
