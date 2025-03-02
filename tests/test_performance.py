import time
import os
from app.core.panel import extract_panels_for_images_in_folder_by_ai
from app.core.model import model


def run_ai_performance_tests() -> None:
    """
    Run AI performance tests
    """

    def get_right_path(path: str) -> str:
        script_dir = os.path.dirname(__file__)
        return os.path.join(script_dir, path)

    test_input_dir = get_right_path("data\\test_performance\\input")
    test_output_dir = get_right_path("data\\test_performance\\output\\ai")

    print("Loading the AI model in prior to tests.")
    model.load()

    print("Running AI performance tests")
    start_time = time.time()
    files, panels = extract_panels_for_images_in_folder_by_ai(
        test_input_dir, test_output_dir
    )
    end_time = time.time()

    execution_time = end_time - start_time
    print(
        f"Execution time: {execution_time} seconds for {files} files and {panels} panels"
    )


def run_tests() -> None:
    """
    Run tests
    """
    run_ai_performance_tests()


if __name__ == "__main__":
    run_tests()
