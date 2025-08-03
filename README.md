# Smart Image Organizer

A Python-based tool for automatically organizing images using metadata (EXIF, date, location) and optional AI-powered tagging.

## Features

- EXIF metadata extraction (date, camera info, GPS coordinates)
- Automatic folder organization by date and location
- Reverse geocoding for location-based organization
- AI-powered image tagging (optional)
- Dry-run mode for previewing changes
- Undo functionality for reverting changes
- Detailed operation logging

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
# Dry run (simulation mode)
python -m src.cli organize /path/to/source /path/to/destination

# Actually organize files
python -m src.cli organize /path/to/source /path/to/destination --no-dry-run

# Use AI tagging
python -m src.cli organize /path/to/source /path/to/destination --use-ai

# Save operations log
python -m src.cli organize /path/to/source /path/to/destination --log operations.json

# Undo operations
python -m src.cli undo operations.json
```

## Directory Structure

The tool organizes images into a directory structure like:
```
destination/
├── 2023/
│   ├── 01/
│   │   ├── New York, USA/
│   │   └── Unknown Location/
│   └── 02/
│       └── Paris, France/
└── Unsorted/
```

## Requirements

- Python 3.8+
- Pillow
- exifread
- typer
- reverse-geocoder
- transformers (for AI tagging)
- rich (for CLI interface)

## License

MIT
