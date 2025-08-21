#!/usr/bin/env python3
"""Fix flake8 issues in the codebase."""
import sys
from pathlib import Path


def fix_auth_py():
    path = Path("src/api/auth.py")
    content = path.read_text()
    content = content.replace(
        "from typing import Optional, Dict", "from typing import Dict"
    )
    content = content.replace(
        "from fastapi import HTTPException, Security, Depends",
        "from fastapi import HTTPException, Security",
    )
    path.write_text(content)


def fix_cache_py():
    path = Path("src/api/cache.py")
    content = path.read_text()
    content = content.replace("import json\n", "")
    path.write_text(content)


def fix_main_py():
    path = Path("src/api/main.py")
    content = path.read_text()
    content = content.replace(
        "from typing import Dict, Optional, List", "from typing import Dict"
    )
    content = content.replace("import json\nimport os\n", "")
    content = content.replace(", Header", "")
    path.write_text(content)


def fix_rate_limiter_py():
    path = Path("src/api/rate_limiter.py")
    content = path.read_text()
    content = content.replace("from datetime import datetime\n", "")
    # Fix long line
    content = content.replace(
        'detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."',
        'detail=f"Rate limit exceeded. Max {self.requests_per_minute} requests/minute."',
    )
    path.write_text(content)


def fix_exif_handler_py():
    path = Path("src/exif_handler.py")
    content = path.read_text()
    content = content.replace(
        "from typing import Dict, Optional, Tuple, Union",
        "from typing import Dict, Optional, Tuple",
    )
    content = content.replace("from datetime import datetime\n", "")
    path.write_text(content)


def fix_test_files():
    # Fix test_ai_tagger.py
    path = Path("tests/test_ai_tagger.py")
    content = path.read_text()
    content = content.replace("import torch\n", "")
    path.write_text(content)

    # Fix test_cli.py
    path = Path("tests/test_cli.py")
    content = path.read_text()
    content = content.replace("from pathlib import Path\n", "")
    content = content.replace("from src.cli import CLIError\n", "")
    path.write_text(content)

    # Fix test_exif_handler.py
    path = Path("tests/test_exif_handler.py")
    content = path.read_text()
    content = content.replace("from pathlib import Path\n", "")
    content = content.replace("from PIL.ExifTags import TAGS, GPSTAGS\n", "")
    content = content.replace("import os\n", "")
    path.write_text(content)

    # Fix test_file_organizer.py
    path = Path("tests/test_file_organizer.py")
    content = path.read_text()
    content = content.replace("from pathlib import Path\n", "")
    path.write_text(content)

    # Fix test_geolocation.py
    path = Path("tests/test_geolocation.py")
    content = path.read_text()
    content = content.replace("from pathlib import Path\n", "")
    path.write_text(content)


def main():
    fix_auth_py()
    fix_cache_py()
    fix_main_py()
    fix_rate_limiter_py()
    fix_exif_handler_py()
    fix_test_files()


if __name__ == "__main__":
    main()
