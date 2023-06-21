import shutil
import os

def pack(output_fp="azenqos_plugin"):
    
    if os.path.exists(output_fp):
        os.remove(output_fp)
    output_fp = os.path.splitext(output_fp)[0]
    source_dir = "Azenqos"
    destination_dir = "azenqos_plugin_bundle/Azenqos"


    if os.path.exists(destination_dir):
        shutil.rmtree(destination_dir)

    # Excluded folders
    excluded_folders = ["test_check_and_recover_db"]

    # Function to determine if a directory should be excluded
    def should_exclude(dir_path):
        return any(folder in dir_path for folder in excluded_folders)

    # Copy the directory tree while excluding specific folders
    for root, dirs, files in os.walk(source_dir, topdown=True):
        # Exclude folders
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]

        # Create corresponding directories in the destination directory
        destination_subdir = os.path.join(destination_dir, os.path.relpath(root, source_dir))
        os.makedirs(destination_subdir, exist_ok=True)

        # Copy files to the destination directory
        for file in files:
            source_file = os.path.join(root, file)
            destination_file = os.path.join(destination_subdir, file)
            shutil.copy2(source_file, destination_file)

    shutil.make_archive(output_fp, "zip", "azenqos_plugin_bundle")