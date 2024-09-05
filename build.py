import os
import glob
import subprocess

def convert_ui_to_py() -> None:
    """
    Convert all .ui files in the src/designer directory to .py files
    into the src/gui directory
    """

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    py_dir = os.path.join("src", "gui")
    ui_dir = os.path.join("src", "designer")
    ui_files = glob.glob(os.path.join(ui_dir, "*.ui"))

    # Create the destination directory if it doesn't exist
    os.makedirs(py_dir, exist_ok=True)

    print(f"Converting {len(ui_files)} .ui files to .py") 

    for ui_file in ui_files:
        # Construct the destination .py file path in src/gui
        py_file_name = os.path.splitext(os.path.basename(ui_file))[0] + ".py"
        py_file = os.path.join(py_dir, py_file_name)
        
        # Command to convert .ui to .py
        command = f"pyuic6 -x {ui_file} -o {py_file}"

        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Converted: {ui_file} -> {py_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error converting {ui_file}: {e}")

if __name__ == "__main__":
    convert_ui_to_py()
