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


def adaptive_vconcat(images: list[np.ndarray], fill_color: tuple[int, int, int] = (255, 255, 255)) -> np.ndarray:
    max_width = max(img.shape[1] for img in images)

    # Resize each image to match the largest dimensions
    resized_images = []
    for img in images:
        resized_img = cv2.copyMakeBorder(img, 
                                         top=0, bottom=0, 
                                         left=0, right=max_width - img.shape[1], 
                                         borderType=cv2.BORDER_CONSTANT, 
                                         value=fill_color)  
        resized_images.append(resized_img)

    # Concatenate vertically
    return np.vstack(resized_images)


def adaptive_hconcat(images: list[np.ndarray], fill_color: tuple[int, int, int] = (255, 255, 255)) -> np.ndarray:
    max_height = max(img.shape[0] for img in images)

    # Resize each image to match the largest dimensions
    resized_images = []
    for img in images:
        resized_img = cv2.copyMakeBorder(img, 
                                         top=0, bottom=max_height - img.shape[0], 
                                         left=0, right=0, 
                                         borderType=cv2.BORDER_CONSTANT, 
                                         value=fill_color)  
        resized_images.append(resized_img)

    # Concatenate horizontally
    return np.hstack(resized_images)


def group_contours_vertically(contours) -> list[list[np.ndarray]]:
    """
    Groups the given contours vertically
    """
    ERROR_THRESHOLD = 0.05
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
    grouped_contours = [[contours[0]]]
    for contour in contours[1:]:
        found_group = False
        contour_x, contour_y, contour_w, contour_h = cv2.boundingRect(contour)
        for group in grouped_contours[::-1]:
            group_x, group_y, group_w, group_h = cv2.boundingRect(group[-1])
            y_diff = abs(contour_y - group_y) - group_h
            if y_diff < 0 or y_diff > min(contour_h, group_h):
                continue 
            group_x_center = group_x + group_w / 2
            contour_x_center = contour_x + contour_w / 2
            if abs(group_x_center - contour_x_center) < ERROR_THRESHOLD * min(group_w, contour_w):
                group.append(contour)
                found_group = True
                break
        if not found_group:
            grouped_contours.append([contour])
    return grouped_contours


def group_contours_horizontally(contours) -> list[list[np.ndarray]]:
    """
    Groups the given contours horizontally
    """
    ERROR_THRESHOLD = 0.05
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
    grouped_contours = [[contours[0]]]
    for contour in contours[1:]:
        found_group = False
        contour_x, contour_y, contour_w, contour_h = cv2.boundingRect(contour)
        for group in grouped_contours[::-1]:
            group_x, group_y, group_w, group_h = cv2.boundingRect(group[-1])
            x_diff = abs(contour_x - group_x) - group_w
            if x_diff < 0 or x_diff > min(contour_w, group_w):
                continue 
            group_y_center = group_y + group_h / 2
            contour_y_center = contour_y + contour_h / 2
            if abs(group_y_center - contour_y_center) < ERROR_THRESHOLD * min(group_h, contour_h):
                group.append(contour)
                found_group = True
                break
        if not found_group:
            grouped_contours.append([contour])
    return grouped_contours