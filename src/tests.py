import time
import os
from image_processing.panel import extract_panels_for_images_in_folder


def runPerformanceTests() -> None:
    def getRightPath(path: str) -> str:
        script_dir = os.path.dirname(__file__)
        return os.path.join(script_dir, path)
    
    def getRightPaths(paths: list[str]) -> list[str]:
        return [getRightPath(path) for path in paths]

    test_input_dir = getRightPath("../test-in")
    test_output_dirs = getRightPaths(["../test-out/base", "../test-out/fallback", "../test-out/split", "../test-out/split-fallback"])

    settings = [0b00, 0b01, 0b10, 0b11]
    settings_string = ["base", "fallback", "split", "split-fallback"]

    print("Running performance tests")

    for i in range(len(test_output_dirs)):
        start_time = time.time()
        files, panels = extract_panels_for_images_in_folder(test_input_dir, test_output_dirs[i], settings[i] & 0b01, settings[i] & 0b10)
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds for {files} files and {panels} panels with {settings_string[i]} settings")

if __name__ == "__main__":
    runPerformanceTests()