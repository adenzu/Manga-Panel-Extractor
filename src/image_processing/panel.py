import os
from typing import Callable
import cv2
import numpy as np
from image_processing.image import is_contour_rectangular, apply_adaptive_threshold
from utils.utils import load_images, load_image
from tqdm import tqdm


def get_background_intensity_range(grayscale_image: np.ndarray, min_range: int = 1) -> tuple[int, int]:
    """
    Returns the minimum and maximum intensity values of the background of the image
    """
    edges = [grayscale_image[-1, :], grayscale_image[0, :], grayscale_image[:, 0], grayscale_image[:, -1]]
    sorted_edges = sorted(edges, key=lambda x: np.var(x))

    least_varied_edge = sorted_edges[0]

    max_intensity = max(least_varied_edge)
    min_intensity = max(min(min(least_varied_edge), max_intensity - min_range), 0)

    return min_intensity, max_intensity


def generate_background_mask(grayscale_image: np.ndarray) -> np.ndarray:
    """
    Generates a mask by focusing on the largest area of white pixels
    """
    WHITE = 255
    LESS_WHITE, _ = get_background_intensity_range(grayscale_image, 25)
    LESS_WHITE = max(LESS_WHITE, 240)

    ret, thresh = cv2.threshold(grayscale_image, LESS_WHITE, WHITE, cv2.THRESH_BINARY)
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)

    mask = np.zeros_like(thresh)

    PAGE_TO_SEGMENT_RATIO = 1024

    halting_area_size = mask.size // PAGE_TO_SEGMENT_RATIO

    mask_height, mask_width = mask.shape
    base_background_size_error_threshold = 0.05
    whole_background_min_width = mask_width * (1 - base_background_size_error_threshold)
    whole_background_min_height = mask_height * (1 - base_background_size_error_threshold)

    for i in np.argsort(stats[1:, 4])[::-1]:
        contour_index = i + 1
        x, y, w, h, area = stats[contour_index]
        if area < halting_area_size:
            break
        if (
            (w > whole_background_min_width) or
            (h > whole_background_min_height) or
            (is_contour_rectangular(cv2.findContours((labels == contour_index).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0][0]))
        ):
            mask[labels == contour_index] = WHITE

    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)

    return mask


def extract_panels(
    image: np.ndarray,
    panel_contours: list[np.ndarray],
    accept_page_as_panel: bool = True,
    mode: str = 'bounding',
    fill_in_color: tuple[int, int, int] = (255, 255, 255),
) -> list[np.ndarray]:
    """
    Extracts panels from the image using the given contours corresponding to the panels
    
    Parameters:
    - image: The image to extract the panels from
    - panel_contours: The contours corresponding to the panels
    - accept_page_as_panel: Whether to accept the whole page as a panel
    - mode: The mode to use for extraction
        - 'contour': Extracts the panels by cuting out only the inside of the contours
        - 'bounding': Extracts the panels by using the bounding boxes of the contours
    - fill_in_color: The color to fill in the background of the panel images
    """
    PAGE_TO_PANEL_RATIO = 32

    height, width = image.shape[:2]
    image_area = width * height
    area_threshold = image_area // PAGE_TO_PANEL_RATIO

    returned_panels = []

    crop_source = image

    if mode == 'contour':
        mask = np.zeros_like(image)
        cv2.drawContours(mask, panel_contours, -1, (255, 255, 255), -1)
        masked_image = cv2.bitwise_and(image, mask)
        masked_image = cv2.bitwise_or(cv2.bitwise_and(cv2.bitwise_not(mask), fill_in_color), masked_image)
        crop_source = masked_image

    for contour in panel_contours:
        x, y, w, h = cv2.boundingRect(contour)

        if not accept_page_as_panel and ((w >= width * 0.99) or (h >= height * 0.99)):
            continue

        area = cv2.contourArea(contour)

        if (area < area_threshold):
            continue

        fitted_panel = crop_source[y:y + h, x:x + w]
        returned_panels.append(fitted_panel)

    return returned_panels


def preprocess_image(grayscale_image: np.ndarray) -> np.ndarray:
    """
    Preprocesses the image for panel extraction
    """
    processed_image = cv2.GaussianBlur(grayscale_image, (3, 3), 0)
    processed_image = cv2.Laplacian(processed_image, -1)
    processed_image = cv2.dilate(processed_image, np.ones((5, 5), np.uint8), iterations=1)
    processed_image = 255 - processed_image
    return processed_image


def joint_panel_split_extraction(grayscale_image: np.ndarray, background_mask: np.ndarray) -> np.ndarray:
    """
    Extracts the panels from the image with splitting the joint panels
    """
    pixels_before = np.count_nonzero(background_mask)
    background_mask = cv2.ximgproc.thinning(background_mask)
    
    up_kernel = np.array([[0, 0, 0], [0, 1, 0], [0, 1, 0]], np.uint8)
    down_kernel = np.array([[0, 1, 0], [0, 1, 0], [0, 0, 0]], np.uint8)
    left_kernel = np.array([[0, 0, 0], [0, 1, 1], [0, 0, 0]], np.uint8)
    right_kernel = np.array([[0, 0, 0], [1, 1, 0], [0, 0, 0]], np.uint8)

    down_right_diagonal_kernel = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 0]], np.uint8)
    down_left_diagonal_kernel = np.array([[0, 0, 1], [0, 1, 0], [0, 0, 0]], np.uint8)
    up_left_diagonal_kernel = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 1]], np.uint8)
    up_right_diagonal_kernel = np.array([[0, 0, 0], [0, 1, 0], [1, 0, 0]], np.uint8)
    
    PAGE_TO_JOINT_OBJECT_RATIO = 3
    image_height, image_width = grayscale_image.shape

    height_based_size = image_height // PAGE_TO_JOINT_OBJECT_RATIO
    width_based_size = (2 * image_width) // PAGE_TO_JOINT_OBJECT_RATIO

    height_based_size += height_based_size % 2 + 1
    width_based_size += width_based_size % 2 + 1

    up_dilation_kernel = np.zeros((height_based_size, height_based_size), np.uint8)
    up_dilation_kernel[height_based_size // 2:, height_based_size // 2] = 1

    down_dilation_kernel = np.zeros((height_based_size, height_based_size), np.uint8)
    down_dilation_kernel[:height_based_size // 2 + 1, height_based_size // 2] = 1

    left_dilation_kernel = np.zeros((width_based_size, width_based_size), np.uint8)
    left_dilation_kernel[width_based_size // 2, width_based_size // 2:] = 1

    right_dilation_kernel = np.zeros((width_based_size, width_based_size), np.uint8)
    right_dilation_kernel[width_based_size // 2, :width_based_size // 2 + 1] = 1

    min_based_size = min(width_based_size, height_based_size)

    down_right_dilation_kernel = np.identity(min_based_size // 2 + 1, dtype=np.uint8)
    down_right_dilation_kernel = np.pad(down_right_dilation_kernel, ((0, min_based_size // 2), (0, min_based_size // 2)))

    up_left_dilation_kernel = np.identity(min_based_size // 2 + 1, dtype=np.uint8)
    up_left_dilation_kernel = np.pad(up_left_dilation_kernel, ((min_based_size // 2, 0), (0, min_based_size // 2)))

    up_right_dilation_kernel = np.flip(np.identity(min_based_size // 2 + 1, dtype=np.uint8), axis=1)
    up_right_dilation_kernel = np.pad(up_right_dilation_kernel, ((min_based_size // 2, 0), (0, min_based_size // 2)))

    down_left_dilation_kernel = np.flip(np.identity(min_based_size // 2 + 1, dtype=np.uint8), axis=1)
    down_left_dilation_kernel = np.pad(down_left_dilation_kernel, ((0, min_based_size // 2), (min_based_size // 2, 0)))

    match_kernels = [
        up_kernel,
        down_kernel,
        left_kernel,
        right_kernel,
        down_right_diagonal_kernel,
        down_left_diagonal_kernel,
        up_left_diagonal_kernel,
        up_right_diagonal_kernel,
    ]

    dilation_kernels = [
        up_dilation_kernel,
        down_dilation_kernel,
        left_dilation_kernel,
        right_dilation_kernel,
        down_right_dilation_kernel,
        down_left_dilation_kernel,
        up_left_dilation_kernel,
        up_right_dilation_kernel,
    ]

    def get_dots(grayscale_image: np.ndarray, kernel: np.ndarray) -> tuple[np.ndarray, int]:
        temp = cv2.matchTemplate(grayscale_image, kernel, cv2.TM_CCOEFF_NORMED)
        _, temp = cv2.threshold(temp, 0.9, 1, cv2.THRESH_BINARY)
        temp = np.where(temp == 1, 255, 0).astype(np.uint8)
        pad_height = (kernel.shape[0] - 1) // 2
        pad_width = (kernel.shape[1] - 1) // 2
        temp = cv2.copyMakeBorder(temp, pad_height, kernel.shape[0] - pad_height - 1, pad_width, kernel.shape[1] - pad_width - 1, cv2.BORDER_CONSTANT, value=0)
        return temp
    
    for match_kernel, dilation_kernel in zip(match_kernels, dilation_kernels):
        dots = get_dots(background_mask, match_kernel)
        lines = cv2.dilate(dots, dilation_kernel, iterations=1)
        background_mask = cv2.bitwise_or(background_mask, lines)

    pixels_now = np.count_nonzero(background_mask)
    dilation_size = pixels_before // (4  * pixels_now)
    dilation_size += dilation_size % 2 + 1
    background_mask = cv2.dilate(background_mask, np.ones((dilation_size, dilation_size), np.uint8), iterations=1)

    page_without_background = 255 - background_mask

    return page_without_background


def threshold_extraction(
        image: np.ndarray, 
        grayscale_image: np.ndarray, 
        mode: str = 'bounding'
) -> list[np.ndarray]:
    """
    Extracts panels from the image using thresholding
    """
    processed_image = cv2.GaussianBlur(grayscale_image, (3, 3), 0)
    processed_image = cv2.Laplacian(processed_image, -1)
    _, thresh = cv2.threshold(processed_image, 8, 255, cv2.THRESH_BINARY)
    processed_image = apply_adaptive_threshold(processed_image)
    processed_image = cv2.subtract(processed_image, thresh)
    processed_image = cv2.dilate(processed_image, np.ones((3, 3), np.uint8), iterations=2)
    contours, _ = cv2.findContours(processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    panels = extract_panels(image, contours, False, mode=mode)

    return panels


def get_page_without_background(grayscale_image: np.ndarray, background_mask: np.ndarray, split_joint_panels = False) -> np.ndarray:
    """
    Returns the page without the background
    """
    STRIPE_FORMAT_MASK_AREA_RATIO = 0.3

    mask_area = np.count_nonzero(background_mask)
    mask_area_ratio = mask_area / background_mask.size

    if STRIPE_FORMAT_MASK_AREA_RATIO > mask_area_ratio and split_joint_panels:
        page_without_background = joint_panel_split_extraction(grayscale_image, background_mask)
    else:
        page_without_background = cv2.subtract(grayscale_image, background_mask)

    return page_without_background


def get_fallback_panels(
        image: np.ndarray, 
        grayscale_image: np.ndarray, 
        fallback: bool, 
        panels: list[np.ndarray],
        mode: str = 'bounding'
) -> list[np.ndarray]:
    """
    Checks if the fallback is needed and returns the appropriate panels
    
    Parameters:
    - mode: The mode to use for extraction
        - 'contour': Extracts the panels by cuting out only the inside of the contours
        - 'bounding': Extracts the panels by using the bounding boxes of the contours
    """
    if fallback and len(panels) < 2:
        tmp = threshold_extraction(image, grayscale_image, mode=mode)
        if len(tmp) > len(panels):
            return tmp
    
    return panels


def generate_panel_blocks(
        image: np.ndarray, 
        background_generator: Callable[[np.ndarray], np.ndarray] = generate_background_mask,
        split_joint_panels: bool = False,
        fallback: bool = True,
        mode: str = 'bounding'
) -> list[np.ndarray]:
    """
    Generates the separate panel images from the base image
    
    Parameters:
    - mode: The mode to use for extraction
        - 'contour': Extracts the panels by cuting out only the inside of the contours
        - 'bounding': Extracts the panels by using the bounding boxes of the contours
    """

    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_image = preprocess_image(grayscale_image)
    background_mask = background_generator(processed_image)
    page_without_background = get_page_without_background(grayscale_image, background_mask, split_joint_panels)
    contours, _ = cv2.findContours(page_without_background, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    panels = extract_panels(image, contours, mode=mode)
    panels = get_fallback_panels(image, grayscale_image, fallback, panels, mode=mode)
        
    return panels


def extract_panels_for_image(image_path: str, output_dir: str, fallback: bool = True, split_joint_panels: bool = False):
    """
    Extracts panels for a single image
    """
    if not os.path.exists(image_path):
        return
    image_path = os.path.abspath(image_path)
    image = load_image(os.path.dirname(image_path), image_path)
    image_name, image_ext = os.path.splitext(image.image_name)
    panel_blocks = generate_panel_blocks(image.image, split_joint_panels=split_joint_panels, fallback=fallback)
    for k, panel in enumerate(tqdm(panel_blocks, total=len(panel_blocks))):
        out_path = os.path.join(output_dir, f"{image_name}_{k}{image_ext}")
        cv2.imwrite(out_path, panel)


def extract_panels_for_images_in_folder(input_dir: str, output_dir: str, fallback: bool = True, split_joint_panels: bool = False):
    """
    Basically the main function of the program,
    this is written with cli usage in mind
    """
    if not os.path.exists(output_dir):
        return (0, 0)
    files = os.listdir(input_dir)
    num_files = len(files)
    num_panels = 0
    for _, image in enumerate(tqdm(load_images(input_dir), total=num_files)):
        image_name, image_ext = os.path.splitext(image.image_name)
        panel_blocks = generate_panel_blocks(image.image, fallback=fallback, split_joint_panels=split_joint_panels)
        for j, panel in enumerate(panel_blocks):
            out_path = os.path.join(output_dir, f"{image_name}_{j}{image_ext}")
            cv2.imwrite(out_path, panel)
        num_panels += len(panel_blocks)
    return (num_files, num_panels)

