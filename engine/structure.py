import os
import shutil as su

from engine import INPUT_DIR, OUTPUT_DIR

# Helper function to create directories and files
def create_file(path, content=""):
    """Create a file and write content to it"""
    with open(path, "w") as f:
        f.write(content)

def create_directories(base_path, structure):
    """Recursively create directories and files based on the structure"""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):  # it's a directory
            os.makedirs(path, exist_ok=True)
            create_directories(path, content)
        else:  # it's a file
            create_file(path, content)

def create_test_directories(root, rel_path, structure):
    """Recursively creates directories and files based on the structure."""
    for name, content in structure.items():
        path = os.path.join(rel_path, "test_" + name)
        abs_path = os.path.join(root, path)
        if (
            isinstance(content, dict)
            and not any(abs_path.endswith(name) for name in ["tests"])
            and len(content.keys()) > 0
        ):  # it's a directory
            os.makedirs(abs_path, exist_ok=True)
            create_test_directories(root, path, content)
        elif isinstance(content, str) and not abs_path.endswith("__init__.py"):
            create_file(abs_path, content)

def mirror_existing_files(project_name):
    pwd = os.getcwd()
    src = os.path.join(pwd, "static")

    # Ensure the destination directory exists
    dst = os.path.join(pwd, OUTPUT_DIR, project_name)
    if not os.path.exists(dst):
        os.makedirs(dst, exist_ok=True)

    # Iterate over files and directories in the current working directory
    for fd in os.listdir(src):
        # Skip the project_name directory and the script itself
        src_path = os.path.join(src, fd)
        dest_path = os.path.join(dst, fd)

        # Check if it's a file or a directory and copy accordingly
        if os.path.isfile(src_path):
            su.copyfile(src_path, dest_path)
        elif os.path.isdir(src_path):
            su.copytree(src_path, dest_path, dirs_exist_ok=True)
