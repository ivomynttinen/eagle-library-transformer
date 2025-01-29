#!/usr/bin/env python3

import os
import json
import shutil
import re
from pathlib import Path
from typing import List, Dict, Set, Optional

# File extension sets
IMAGE_EXTENSIONS: Set[str] = {
    '.bmp', '.gif', '.heic', '.heif', '.hif', '.icns', '.ico', '.jpeg', '.jpg', 
    '.png', '.svg', '.tif', '.tiff', '.webp', '.avif', '.base64', '.jfif', 
    '.insp', '.jxl', '.jpe'
}

SUPPORTED_EXTENSIONS: Set[str] = {
    # Images
    *IMAGE_EXTENSIONS,
    # 3D
    '.fbx', '.obj', '.3ds', '.3mf', '.dae', '.ifc', '.ply', '.stl', '.glb',
    # Textures
    '.dds', '.exr', '.hdr', '.tga',
    # Source files
    '.afdesign', '.afphoto', '.afpub', '.ai', '.c4d', '.cdr', '.clip', '.dwg',
    '.graffle', '.idml', '.indd', '.indt', '.mindnode', '.psb', '.psd', '.psdt',
    '.pxd', '.principle', '.sketch', '.skt', '.skp', '.xd', '.xmind',
    # Video
    '.m4v', '.mp4', '.webm', '.mov',
    # Audio
    '.aac', '.flac', '.m4a', '.mp3', '.ogg', '.wav',
    # Fonts
    '.ttf', '.ttc', '.otf', '.woff',
    # RAW
    '.3fr', '.arw', '.cr2', '.cr3', '.crw', '.dng', '.erf', '.mrw', '.nef',
    '.nrw', '.orf', '.otf', '.pef', '.raf', '.raw', '.rw2', '.sr2', '.srw', '.x3f',
    # Office
    '.txt', '.key', '.numbers', '.pages', '.pdf', '.potx', '.ppt', '.pptx',
    '.xls', '.xlsx', '.doc', '.docx', '.eddx', '.emmx',
    # Others
    '.html', '.mhtml', '.url'
}

def normalize_filename(filename: str, item_id: str) -> str:
    """Normalize filename by removing special characters and replacing spaces with hyphens."""
    name, ext = os.path.splitext(filename)
    normalized = re.sub(r'[^a-zA-Z0-9-]', '', name.replace(' ', '-'))
    return f"{normalized.lower()}-{item_id}{ext.lower()}"

def get_file_type(suffix: str) -> str:
    """Determine the type of file based on its suffix."""
    return 'image' if suffix.lower() in IMAGE_EXTENSIONS else 'other'

def get_user_preference() -> bool:
    """Get user preference for processing only images."""
    while True:
        images_only = input("Process only image files? (y/N): ").lower()
        if images_only in ['y', 'n', '']:
            return images_only == 'y'
        print("Please enter 'y' for yes or 'n' (or press Enter) for no")

def setup_directories() -> tuple[Path, Path]:
    """Create and return necessary directory paths."""
    dist_path = Path('dist')
    images_path = dist_path / 'images'
    dist_path.mkdir(exist_ok=True)
    images_path.mkdir(exist_ok=True)
    return dist_path, images_path

def load_metadata(metadata_file: Path) -> Optional[Dict]:
    """Load and return metadata from json file."""
    try:
        return json.loads(metadata_file.read_text())
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {metadata_file}")
        return None
    except Exception as e:
        print(f"Error reading {metadata_file}: {e}")
        return None

def load_library_metadata() -> Dict:
    """Load the main library metadata file containing folder information."""
    library_metadata_path = Path('library/metadata.json')
    try:
        return json.loads(library_metadata_path.read_text())
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading library metadata: {e}")
        return {"folders": []}

def build_folder_map(folders: List[Dict], folder_map: Dict = None) -> Dict[str, str]:
    """Build a mapping of folder IDs to folder names, including nested folders."""
    if folder_map is None:
        folder_map = {}
    
    for folder in folders:
        if folder.get("password"):  # Skip folders with passwords
            continue
        folder_map[folder["id"]] = folder["name"]
        if folder.get("children"):
            build_folder_map(folder["children"], folder_map)
    
    return folder_map

def process_file(file_path: Path, images_path: Path, metadata: Dict, 
                images_only: bool) -> tuple[bool, Optional[Dict]]:
    """Process a single file and return (success, updated_metadata)."""
    if (file_path.name == 'metadata.json' or 
        'thumbnail' in file_path.name.lower() or
        file_path.suffix.lower() not in SUPPORTED_EXTENSIONS):
        return False, None

    # Ensure we have valid metadata with an ID
    if not isinstance(metadata, dict) or 'id' not in metadata:
        print(f"Warning: Missing or invalid metadata for {file_path}")
        return False, None

    file_type = get_file_type(file_path.suffix)
    if images_only and file_type != 'image':
        return False, None

    new_filename = normalize_filename(file_path.name, metadata['id'])
    new_path = images_path / new_filename

    try:
        shutil.copy2(str(file_path), str(new_path))
    except (shutil.SameFileError, OSError) as e:
        print(f"Warning: Could not copy {file_path}: {e}")
        return False, None

    metadata = metadata.copy()
    metadata['filename'] = new_filename
    metadata['file_type'] = file_type
    return True, metadata

def process_library() -> None:
    """Main function to process the library files."""
    images_only = get_user_preference()
    dist_path, images_path = setup_directories()
    
    library_path = Path('library/images')
    if not library_path.exists():
        print(f"Error: {library_path} directory not found!")
        return

    # Load library metadata and build folder map
    library_metadata = load_library_metadata()
    folder_map = build_folder_map(library_metadata.get("folders", []))

    consolidated_metadata = []
    processed_files = skipped_files = deleted_files = 0
    
    for subdir in (d for d in library_path.iterdir() if d.is_dir()):
        metadata_file = subdir / 'metadata.json'
        if not metadata_file.exists():
            print(f"Warning: No metadata.json found in {subdir}")
            continue

        metadata = load_metadata(metadata_file)
        if metadata is None:
            continue

        # Skip deleted entries
        if metadata.get("isDeleted"):
            deleted_files += 1
            continue

        # Replace folder IDs with names
        if "folders" in metadata:
            folder_names = []
            for folder_id in metadata["folders"]:
                if folder_id in folder_map:
                    folder_names.append(folder_map[folder_id])
            metadata["folders"] = folder_names

        for file_path in subdir.iterdir():
            success, updated_metadata = process_file(
                file_path, images_path, metadata, images_only
            )
            
            if success:
                processed_files += 1
                if updated_metadata:
                    consolidated_metadata.append(updated_metadata)
            elif images_only and get_file_type(file_path.suffix) != 'image':
                skipped_files += 1

    # Write consolidated metadata
    (dist_path / 'metadata.json').write_text(
        json.dumps(consolidated_metadata, indent=2)
    )

    print("\nProcessing complete!")
    print(f"Processed {processed_files} files")
    if images_only:
        print(f"Skipped {skipped_files} non-image files")
    print(f"Skipped {deleted_files} deleted files")
    print(f"Created {len(consolidated_metadata)} metadata entries")
    print("Consolidated metadata saved to dist/metadata.json")
    print("Original library files remain unchanged")

if __name__ == '__main__':
    process_library() 
