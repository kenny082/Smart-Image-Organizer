"""
ExifHandler module for extracting and processing EXIF metadata from images.

This module provides functionality to:
- Extract EXIF metadata from image files
- Parse date information
- Extract and convert GPS coordinates
- Get camera information

Example:
    handler = ExifHandler()
    exif_data = handler.get_exif_data(image_path)
    date = handler.get_date_taken(exif_data)
    coords = handler.get_gps_coordinates(exif_data)
    camera_info = handler.get_camera_info(exif_data)
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


class ExifHandler:
    """
    A class to handle EXIF metadata extraction and processing from images.

    This class provides methods to extract and process various types of EXIF metadata
    including dates, GPS coordinates, and camera information.
    """

    def __init__(self) -> None:
        """Initialize the ExifHandler with a configured logger."""
        self.logger = logging.getLogger(__name__)

    def get_exif_data(self, image_path: Path) -> Dict[str, Any]:
        """Extract EXIF data from an image file.

        Args:
            image_path (Path): Path to the image file.

        Returns:
            Dict: Dictionary containing EXIF data. Empty if no data or error.
                 Keys are tag names, values are tag values.

        Examples:
            >>> handler = ExifHandler()
            >>> exif_data = handler.get_exif_data(Path("image.jpg"))
            >>> print(exif_data.get("Make"))  # Get camera manufacturer
            'SONY'
        """
        # Convert to Path object if needed
        try:
            image_path = Path(str(image_path))
        except TypeError:
            self.logger.error(f"Invalid path type: {type(image_path)}")
            return {}

        if not image_path.exists():
            self.logger.error(f"Image file does not exist: {image_path}")
            return {}

        if not image_path.is_file():
            self.logger.error(f"Path is not a file: {image_path}")
            return {}

        try:
            with Image.open(image_path) as img:
                # Check if image format supports EXIF
                if img.format not in ("JPEG", "TIFF", "HEIC"):
                    self.logger.warning(
                        f"Image format {img.format} may not support EXIF data"
                    )

                exif = img._getexif()
                if not exif:
                    self.logger.debug(f"No EXIF data found in {image_path}")
                    return {}

                exif_data = {}
                for tag_id, value in exif.items():
                    try:
                        tag = TAGS.get(tag_id, tag_id)
                        # Handle binary data
                        if isinstance(value, bytes):
                            continue
                        exif_data[tag] = value
                    except Exception as e:
                        self.logger.debug(
                            f"Error processing EXIF tag {tag_id}: {str(e)}"
                        )
                        continue

                # Extract GPS info if available
                if "GPSInfo" in exif_data:
                    try:
                        gps_data = {}
                        for tag_id, value in exif_data["GPSInfo"].items():
                            tag = GPSTAGS.get(tag_id, tag_id)
                            gps_data[tag] = value
                        exif_data["GPSInfo"] = gps_data
                    except Exception as e:
                        self.logger.warning(f"Error processing GPS data: {str(e)}")
                        exif_data.pop("GPSInfo", None)

                return exif_data

        except Image.UnidentifiedImageError:
            self.logger.error(f"Cannot identify image file: {image_path}")
            return {}
        except Exception as e:
            self.logger.warning(f"Failed to extract EXIF from {image_path}: {str(e)}")
            return {}

    def get_date_taken(self, exif_data: Dict[str, Any]) -> Optional[str]:
        """Extract the date taken from EXIF data."""
        date_fields = ["DateTimeOriginal", "DateTimeDigitized", "DateTime"]

        for field in date_fields:
            if field in exif_data:
                value = exif_data[field]
                return str(value) if value is not None else None
        return None

    def get_gps_coordinates(self, exif_data: Dict) -> Optional[Tuple[float, float]]:
        """Extract GPS coordinates from EXIF data."""
        try:
            if "GPSInfo" not in exif_data:
                return None

            gps_info = exif_data["GPSInfo"]

            has_lat = "GPSLatitude" in gps_info
            has_lon = "GPSLongitude" in gps_info
            if has_lat and has_lon:
                lat = self._convert_to_degrees(gps_info["GPSLatitude"])
                lon = self._convert_to_degrees(gps_info["GPSLongitude"])

                if gps_info["GPSLatitudeRef"] == "S":
                    lat = -lat
                if gps_info["GPSLongitudeRef"] == "W":
                    lon = -lon

                return (lat, lon)

        except Exception as e:
            self.logger.warning(f"Failed to extract GPS coordinates: {str(e)}")
        return None

    def _convert_to_degrees(self, value: Tuple[float, float, float]) -> float:
        """Helper function to convert GPS coordinates to degrees."""
        d, m, s = value
        return float(d + (m / 60.0) + (s / 3600.0))

    def get_camera_info(self, exif_data: Dict) -> Dict[str, str]:
        """Retrieve camera information from EXIF data.

        Extracts camera-related metadata including make, model, lens info, and settings.

        Args:
            exif_data: A dictionary containing EXIF metadata.

        Returns:
            A dictionary containing camera information with standardized field names.
        """
        camera_info = {}
        camera_fields = {
            "Make": "make",
            "Model": "model",
            "LensModel": "lens",
            "FNumber": "f_number",
            "ExposureTime": "exposure",
            "ISOSpeedRatings": "iso",
        }

        for exif_field, info_field in camera_fields.items():
            if exif_field in exif_data:
                camera_info[info_field] = str(exif_data[exif_field])

        return camera_info
