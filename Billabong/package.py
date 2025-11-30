
import os
import shutil
import zipfile

PLUGIN_NAME = "Billabong"
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(SRC_DIR, "dist")
PLUGIN_DIR = os.path.join(DIST_DIR, PLUGIN_NAME)

# Files/Folders to INCLUDE
INCLUDES = [
    "metadata.txt",
    "__init__.py",
    "LICENSE",
    "README.md",
    "icon.png",
    "src",
    "data",
    "img",
    "resources",
    "docs" # Optional but good practice
]

# Files/Extensions to EXCLUDE (within included directories)
EXCLUDE_EXT = [".pyc", ".pyo", ".git", ".gitignore", ".DS_Store"]
EXCLUDE_DIRS = ["__pycache__", ".idea", ".vscode", ".git"]

def ignore_patterns(path, names):
    keep = []
    for name in names:
        if name in EXCLUDE_DIRS:
            keep.append(name)
        elif any(name.endswith(ext) for ext in EXCLUDE_EXT):
            keep.append(name)
    return set(keep)

def package():
    # Clean dist
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(PLUGIN_DIR)
    
    print(f"Packaging {PLUGIN_NAME}...")
    
    for item in INCLUDES:
        src = os.path.join(SRC_DIR, item)
        dst = os.path.join(PLUGIN_DIR, item)
        
        if not os.path.exists(src):
            print(f"Warning: {item} not found, skipping.")
            continue
            
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=ignore_patterns)
        else:
            shutil.copy2(src, dst)
            
    # Create Zip
    zip_name = os.path.join(DIST_DIR, f"{PLUGIN_NAME}.zip")
    shutil.make_archive(os.path.join(DIST_DIR, PLUGIN_NAME), 'zip', DIST_DIR, PLUGIN_NAME)
    
    print(f"\nSuccess! Zip created at: {zip_name}")
    print("You can upload this file to plugins.qgis.org")

if __name__ == "__main__":
    package()
