from pathlib import Path
from typing import Dict, List, Optional
import shutil
import json
import logging
from datetime import datetime
from .exif_handler import ExifHandler
from .geolocation import GeoLocationHandler
from .ai_tagger import AITagger


class FileOrganizer:
    def __init__(self, source_dir: Path, dest_dir: Path, use_ai: bool = False):
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.exif_handler = ExifHandler()
        self.geo_handler = GeoLocationHandler()
        self.ai_tagger = AITagger() if use_ai else None
        self.logger = logging.getLogger(__name__)
        self.operations_log: List[Dict[str, Optional[str]]] = []

    def scan_images(self) -> List[Path]:
        """Scan source directory for image files."""
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
        return [
            f
            for f in self.source_dir.rglob("*")
            if f.suffix.lower() in image_extensions
        ]

    def organize_images(self, dry_run: bool = True) -> Dict:
        """
        Organize images based on their metadata.
        Args:
            dry_run: If True, only simulate the operations
        Returns:
            Dictionary with operation statistics
        """
        stats = {"processed": 0, "moved": 0, "tagged": 0, "errors": 0}
        self.operations_log = []

        for image_path in self.scan_images():
            try:
                exif_data = self.exif_handler.get_exif_data(image_path)

                # Get date and location information
                date_taken = self.exif_handler.get_date_taken(exif_data)
                coords = self.exif_handler.get_gps_coordinates(exif_data)
                location_info = (
                    self.geo_handler.get_location_info(coords) if coords else None
                )

                # Generate new path
                new_path = self._generate_new_path(
                    image_path, date_taken, location_info
                )

                # Generate AI tags if enabled
                tags = None
                if self.ai_tagger is not None:
                    tags = self.ai_tagger.generate_tags(image_path)
                    if tags:
                        stats["tagged"] += 1

                if not dry_run:
                    self._move_file(image_path, new_path)
                    if tags:
                        self.ai_tagger.save_tags(new_path, tags)

                self.operations_log.append(
                    {
                        "source": str(image_path),
                        "destination": str(new_path),
                        "date_taken": date_taken,
                        "location": (
                            self.geo_handler.format_location_string(location_info)
                            if location_info
                            else None
                        ),
                        "tags": tags,
                    }
                )

                stats["moved"] += 1

            except Exception as e:
                self.logger.error(f"Error processing {image_path}: {str(e)}")
                stats["errors"] += 1

            stats["processed"] += 1

        return stats

    def _generate_new_path(
        self, image_path: Path, date_taken: Optional[str], location_info: Optional[Dict]
    ) -> Path:
        """Generate new path for the image based on metadata."""
        try:
            # Parse date or use file modification time as fallback
            if date_taken:
                date = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
            else:
                date = datetime.fromtimestamp(image_path.stat().st_mtime)

            # Create directory structure
            year_month = date.strftime("%Y/%m")

            if location_info:
                location_str = self.geo_handler.format_location_string(location_info)
                new_dir = self.dest_dir / year_month / location_str
            else:
                new_dir = self.dest_dir / year_month / "Unknown_Location"

            # Ensure unique filename
            new_path = new_dir / image_path.name
            counter = 1
            while new_path.exists():
                new_path = new_dir / f"{image_path.stem}_{counter}{image_path.suffix}"
                counter += 1

            return new_path

        except Exception as e:
            self.logger.error(f"Error generating new path for {image_path}: {str(e)}")
            return self.dest_dir / "Unsorted" / image_path.name

    def _move_file(self, source: Path, dest: Path) -> None:
        """Safely move a file to its new location."""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(dest))
        except Exception as e:
            self.logger.error(f"Error moving {source} to {dest}: {str(e)}")
            raise

    def save_operations_log(self, output_path: Path) -> None:
        """Save the operations log to a JSON file."""
        try:
            with open(output_path, "w") as f:
                json.dump(self.operations_log, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving operations log: {str(e)}")

    def undo_operations(self) -> None:
        """Undo the last batch of file operations."""
        for operation in reversed(self.operations_log):
            try:
                source = Path(operation["destination"])
                dest = Path(operation["source"])

                if source.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(dest))

                    # Remove tags file if it exists
                    tags_file = source.with_suffix(".json")
                    if tags_file.exists():
                        tags_file.unlink()

            except Exception as e:
                self.logger.error(f"Error undoing operation {operation}: {str(e)}")
