import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import platform

def download_exiftool_windows(dest_dir):
    url = "https://sourceforge.net/projects/exiftool/files/exiftool-13.33_64.zip/download"
    zip_path = os.path.join(dest_dir, "exiftool.zip")
    print("Downloading ExifTool for Windows...")
    urllib.request.urlretrieve(url, zip_path)
    print("Download complete.")

    print("Extracting ExifTool...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)
    os.remove(zip_path)

    exiftool_dir = None
    exiftool_k_path = None
    for root, dirs, files in os.walk(dest_dir):
        for file in files:
            if file.lower() == "exiftool(-k).exe":
                exiftool_k_path = os.path.join(root, file)
                exiftool_dir = root
                break
        if exiftool_k_path:
            break

    if exiftool_k_path is None:
        print("Error: extracted ExifTool executable not found.")
        sys.exit(1)

    exiftool_path = os.path.join(exiftool_dir, "exiftool.exe")
    if not os.path.exists(exiftool_path):
        # Copy or rename exiftool(-k).exe to exiftool.exe
        shutil.copy2(exiftool_k_path, exiftool_path)
    print(f"Extraction complete. Using ExifTool executable at: {exiftool_path}")

    return exiftool_path


def find_exiftool(script_dir):
    system = platform.system()
    if system == "Windows":
        # Check if exiftool already extracted (look for any folder containing exiftool(-k).exe)
        exiftool_path = None
        for root, dirs, files in os.walk(script_dir):
            for file in files:
                if file.lower() == "exiftool(-k).exe":
                    exiftool_path = os.path.join(root, file)
                    break
            if exiftool_path:
                break

        if exiftool_path is None:
            # Download and extract
            exiftool_path = download_exiftool_windows(script_dir)
        return exiftool_path
    else:
        from shutil import which
        exiftool_path = which("exiftool")
        if exiftool_path is None:
            print("ExifTool not found on your system. Please install it manually.")
            print("On macOS: brew install exiftool")
            print("On Linux (Debian/Ubuntu): sudo apt install libimage-exiftool-perl")
            sys.exit(1)
        return exiftool_path

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(script_dir, "target")

    if not os.path.isdir(target_dir):
        print(f"Target directory not found. Creating: {target_dir}")
        os.makedirs(target_dir)
        print("Target directory created. Please place your images inside it and re-run the script.")
        sys.exit(0)

    os.chdir(target_dir)
    print(f"Processing images in: {target_dir}")

    exiftool = find_exiftool(script_dir)

    extensions = ['.jpg', '.jpeg', '.png', '.tiff']

    files = [f for f in os.listdir(target_dir)
             if os.path.isfile(f) and os.path.splitext(f)[1].lower() in extensions]

    if not files:
        print("No image files found to process.")
        return

    print(f"Removing metadata from {len(files)} files...")
    subprocess.run(
        [exiftool, "-all=", "-overwrite_original"] + files,
        check=True
    )

    print("Metadata removal complete.")

if __name__ == "__main__":
    main()
