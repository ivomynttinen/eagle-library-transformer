#!/usr/bin/env python3

import os
import json
import shutil
import re
from pathlib import Path

def normalize_filename(filename):
    """Normalize filename by removing special characters and replacing spaces with hyphens."""
    # Get the name and extension separately
    name, ext = os.path.splitext(filename)
    # Replace spaces with hyphens and remove special characters
    normalized = re.sub(r'[^a-zA-Z0-9-]', '', name.replace(' ', '-'))
    return f"{normalized.lower()}{ext.lower()}"

def process_library():
    # Create output directories if they don't exist
    dist_path = Path('dist')
    dist_path.mkdir(exist_ok=True)
    images_path = dist_path / 'images'
    images_path.mkdir(exist_ok=True)
    
    library_path = Path('library/images')
    if not library_path.exists():
        print(f"Error: {library_path} directory not found!")
        return

    consolidated_metadata = []
    
    # Walk through all subdirectories in the library
    for subdir in library_path.iterdir():
        if not subdir.is_dir():
            continue

        metadata_file = subdir / 'metadata.json'
        if not metadata_file.exists():
            print(f"Warning: No metadata.json found in {subdir}")
            continue

        # Read metadata
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {metadata_file}")
            continue

        # Process media files in the directory
        for file_path in subdir.iterdir():
            if file_path.name == 'metadata.json':
                continue

            # Skip thumbnails
            if 'thumbnail' in file_path.name.lower():
                continue

            # Check if it's a media file (all file types that Eagle supports [https://en.eagle.cool/article/184-what-file-formats-does-eagle-support])
            if file_path.suffix.lower() in [
                # Images
                '.bmp', '.gif', '.heic', '.heif', '.hif', '.icns', '.ico', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff', '.ttf', '.webp', '.avif', '.base64', '.jfif', '.insp', '.jxl', '.jpe',
                # 3D
                '.fbx', '.obj', '.3ds', '.3mf', '.dae', '.ifc', '.ply', '.stl', '.glb',
                # Textures
                '.dds', '.exr', '.hdr', '.tga',
                # Source files
                '.afdesign', '.afphoto', '.afpub', '.ai', '.c4d', '.cdr', '.clip', '.dwg', '.graffle', '.idml', '.indd', '.indt', '.mindnode', '.psb', '.psd', '.psdt', '.pxd', '.principle', '.sketch', '.skt', '.skp', '.xd', '.xmind',
                # Video
                '.m4v', '.mp4', '.webm', '.mov',
                # Audio
                '.aac', '.flac', '.m4a', '.mp3', '.ogg', '.wav',
                # Fonts
                '.ttf', '.ttc', '.otf', '.woff',
                # RAW
                '.3fr', '.arw', '.cr2', '.cr3', '.crw', '.dng', '.erf', '.mrw', '.nef', '.nrw', '.orf', '.otf', '.pef', '.raf', '.raw', '.rw2', '.sr2', '.srw', '.x3f',
                # Office
                '.txt', '.key', '.numbers', '.pages', '.pdf', '.potx', '.ppt', '.pptx', '.xls', '.xlsx', '.doc', '.docx', '.eddx', '.emmx',
                # Others
                '.html', '.mhtml', '.url'
            ]:
                # Normalize filename
                new_filename = normalize_filename(file_path.name)
                new_path = images_path / new_filename

                # Move file to images directory
                shutil.move(str(file_path), str(new_path))

                # Update metadata with new filename
                if isinstance(metadata, dict):
                    metadata['filename'] = new_filename
                else:
                    print(f"Warning: Unexpected metadata format in {metadata_file}")

        consolidated_metadata.append(metadata)

    # Write consolidated metadata
    with open(dist_path / 'metadata.json', 'w') as f:
        json.dump(consolidated_metadata, f, indent=2)

    print("Processing complete!")
    print(f"Processed {len(consolidated_metadata)} metadata files")
    print("Consolidated metadata saved to dist/metadata.json")

if __name__ == '__main__':
    process_library() 
