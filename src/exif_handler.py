from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

class ExifHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_exif_data(self, image_path: Path) -> Dict:
        """Extract EXIF data from an image file."""
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()
                if not exif:
                    return {}
                
                exif_data = {}
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value

                # Extract GPS info if available
                if "GPSInfo" in exif_data:
                    gps_data = {}
                    for tag_id, value in exif_data["GPSInfo"].items():
                        tag = GPSTAGS.get(tag_id, tag_id)
                        gps_data[tag] = value
                    exif_data["GPSInfo"] = gps_data

                return exif_data

        except Exception as e:
            self.logger.warning(f"Failed to extract EXIF from {image_path}: {str(e)}")
            return {}

    def get_date_taken(self, exif_data: Dict) -> Optional[str]:
        """Extract the date taken from EXIF data."""
        date_fields = ["DateTimeOriginal", "DateTimeDigitized", "DateTime"]
        
        for field in date_fields:
            if field in exif_data:
                return exif_data[field]
        return None

    def get_gps_coordinates(self, exif_data: Dict) -> Optional[Tuple[float, float]]:
        """Extract GPS coordinates from EXIF data."""
        try:
            if "GPSInfo" not in exif_data:
                return None

            gps_info = exif_data["GPSInfo"]
            
            if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
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

    def _convert_to_degrees(self, value: Tuple) -> float:
        """Helper function to convert GPS coordinates to degrees."""
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)

    def get_camera_info(self, exif_data: Dict) -> Dict[str, str]:
        """Extract camera information from EXIF data."""
        camera_info = {}
        camera_fields = {
            "Make": "make",
            "Model": "model",
            "LensModel": "lens",
            "FNumber": "f_number",
            "ExposureTime": "exposure",
            "ISOSpeedRatings": "iso"
        }
        
        for exif_field, info_field in camera_fields.items():
            if exif_field in exif_data:
                camera_info[info_field] = str(exif_data[exif_field])
        
        return camera_info
