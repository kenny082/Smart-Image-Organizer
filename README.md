# Smart Image Organizer

A Python-based tool for automatically organizing images using metadata (EXIF, date, location) and optional AI-powered tagging.

[![Tests](https://github.com/kenny082/Smart-Image-Organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/kenny082/Smart-Image-Organizer/actions/workflows/tests.yml)
[![Code Quality](https://github.com/kenny082/Smart-Image-Organizer/actions/workflows/code-quality.yml/badge.svg)](https://github.com/kenny082/Smart-Image-Organizer/actions/workflows/code-quality.yml)
[![codecov](https://codecov.io/gh/kenny082/Smart-Image-Organizer/branch/main/graph/badge.svg)](https://codecov.io/gh/kenny082/Smart-Image-Organizer)

## Features

- **Metadata Extraction**: Extract EXIF data including dates, camera info, and GPS coordinates
- **Smart Organization**: Automatically organize by date and location
- **Location Recognition**: Convert GPS coordinates to readable location names
- **AI Tagging**: Optional AI-powered image content tagging
- **Safe Operations**:
  - Dry-run mode for previewing changes
  - Preview command to see planned operations
  - Undo functionality for reverting changes
  - Detailed operation logging
- **User-Friendly Interface**:
  - Progress bars with time estimation
  - Clear error messages
  - Operation summaries

## Installation

### For Users

1. Install from PyPI (recommended):
```bash
pip install smart-image-organizer
```

2. Or install from source:
```bash
git clone https://github.com/kenny082/Smart-Image-Organizer.git
cd Smart-Image-Organizer
pip install .
```

### For Developers

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development setup instructions.

Quick setup:
```bash
git clone https://github.com/kenny082/Smart-Image-Organizer.git
cd Smart-Image-Organizer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r dev-requirements.txt
pip install -e .
```

## Usage

### Basic Commands

```bash
# Preview organization (no changes made)
smart-organize preview /path/to/source /path/to/destination

# Dry run simulation
smart-organize organize /path/to/source /path/to/destination

# Actually organize files
smart-organize organize /path/to/source /path/to/destination --no-dry-run

# Use AI tagging
smart-organize organize /path/to/source /path/to/destination --use-ai

# Save operations log
smart-organize organize /path/to/source /path/to/destination --log operations.json

# Undo operations
smart-organize undo operations.json
```

### Directory Structure

The tool organizes images into a structured format:
```
destination/
├── 2023/
│   ├── 01/
│   │   ├── New York, USA/
│   │   │   ├── IMG_0001.jpg
│   │   │   └── IMG_0002.jpg
│   │   └── Unknown Location/
│   │       └── IMG_0003.jpg
│   └── 02/
│       └── Paris, France/
│           └── IMG_0004.jpg
└── Unsorted/
    └── corrupted_image.jpg
```

## Requirements

- Python 3.8 or higher
- Core dependencies:
  - Pillow: Image processing
  - exifread: EXIF metadata extraction
  - typer: CLI interface
  - reverse-geocoder: Location lookup
  - rich: Terminal formatting and progress bars
- Optional dependencies:
  - transformers: AI image tagging
  - torch: Required for AI tagging

## CI note

- To avoid heavy model downloads and speed up CI, set the environment variable `SIO_DISABLE_AI=1` in your CI environment. This disables AI tagging during tests while keeping the rest of the functionality intact.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development environment setup
- Testing instructions
- Code style guidelines
- CI/CD pipeline details

## License

MIT License - see [LICENSE](LICENSE) for details
