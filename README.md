# Eagle Library Transformer

This Python script processes a library of images and their metadata, consolidating them into a single organized structure.

## Features

- Consolidates multiple metadata.json files into a single JSON file
- Normalizes image and video filenames (removes spaces and special characters)
- Moves all media files (except thumbnails) into a centralized images directory
- Maintains relationships between metadata and media files

## Requirements

- Python 3.x
- No additional dependencies required (uses only standard library)

## Directory Structure

```
.
├── library/               # Source directory (git ignored)
│   └── images/
│       └── [various subfolders]/
│           ├── metadata.json
│           └── [image/video files]
├── dist/                # Output directory (git ignored)
│   ├── images/          # Contains all processed media files
│   └── metadata.json    # Consolidated metadata file
├── transform.py
└── README.md
```

## Usage

1. Ensure your library structure is set up as shown above
2. Run the script:

```bash
python3 transform.py
```

## Output

The script will:
1. Create a consolidated `metadata.json` file in the `dist` directory
2. Move and rename all media files (except thumbnails) to the `dist/images` directory
3. Update file references in the metadata to match the new file locations 
