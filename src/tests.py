import time
import os
from image_processing.panel import extract_panels_for_images_in_folder, MergeMode, extract_panels_for_images_in_folder_by_ai


def run_ai_performance_tests() -> None:
    """
    Run AI performance tests
    """
    def get_right_path(path: str) -> str:
        script_dir = os.path.dirname(__file__)
        return os.path.join(script_dir, path)

    test_input_dir = get_right_path("../test-in")
    test_output_dir = get_right_path("../test-out/ai")

    print("Running AI performance tests")
    start_time = time.time()
    files, panels = extract_panels_for_images_in_folder_by_ai(test_input_dir, test_output_dir)
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds for {files} files and {panels} panels")


def run_performance_tests() -> None:
    """
    Run performance tests
    """
    def get_right_path(path: str) -> str:
        script_dir = os.path.dirname(__file__)
        return os.path.join(script_dir, path)
    
    def get_right_paths(paths: list[str]) -> list[str]:
        return [get_right_path(path) for path in paths]

    test_input_dir = get_right_path("../test-in")
    test_output_dirs = get_right_paths([
        "../test-out/base", 
        "../test-out/base-vertical",
        "../test-out/base-horizontal",
        "../test-out/fallback", 
        "../test-out/split", 
        "../test-out/split-fallback",
        ])

    settings = [0b0000, 0b0100, 0b1000, 0b0001, 0b0010, 0b0011]
    settings_string = ["base", "base-vertical", "base-horizontal", "fallback", "split", "split-fallback"]

    merge_settings = {
        0b0000: MergeMode.NONE,
        0b0100: MergeMode.VERTICAL,
        0b1000: MergeMode.HORIZONTAL,
    }

    print("Running performance tests")
    for i in range(len(test_output_dirs)):
        start_time = time.time()
        files, panels = extract_panels_for_images_in_folder(test_input_dir, test_output_dirs[i], settings[i] & 0b01, settings[i] & 0b10, merge=merge_settings[settings[i] & 0b1100])
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds for {files} files and {panels} panels with {settings_string[i]} settings")


def run_tests() -> None:
    """
    Run tests
    """
    run_ai_performance_tests()
    run_performance_tests()


if __name__ == "__main__":
    run_tests()