# Eagle Library Transformer

This Python script processes a library of images and their metadata, consolidating them into a single organized structure.

Guide of how to turn an Eagle library into a web hostable format: [Publishing Eagle App Library on the Web](https://ivomynttinen.com/blog/publishing-eagle-app-library-on-the-web-part-1/)

## Features

- Consolidates multiple metadata.json files into a single JSON file
- Copies and normalizes media files to a centralized location
- Preserves original library structure (files are copied, not moved)
- Normalizes filenames (removes spaces and special characters)
- Maintains relationships between metadata and media files
- Option to process only image files, excluding other media types
- Adds file type information to metadata

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
├── dist/                 # Output directory (git ignored)
│   ├── images/          # Contains copies of processed media files
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

3. When prompted, choose whether to process only image files:
   - Enter 'y' to process only images (skips videos, documents, and other media)
   - Enter 'n' or press Enter to process all supported media files

## Output

The script will:
1. Create a consolidated `metadata.json` file in the `dist` directory
2. Copy and rename media files (except thumbnails) to the `dist/images` directory
3. Update file references in the metadata to match the new file locations
4. Add file type information to each metadata entry
5. Leave all original files in the library directory unchanged
