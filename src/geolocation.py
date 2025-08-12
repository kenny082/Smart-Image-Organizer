import reverse_geocoder
from typing import Dict, Optional, Tuple
import logging

class GeoLocationHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_location_info(self, coordinates: Tuple[float, float]) -> Optional[Dict]:
        """
        Get location information from GPS coordinates using reverse geocoding.
        Args:
            coordinates: Tuple of (latitude, longitude)
        Returns:
            Dictionary containing location information or None if failed
        """
        try:
            # Validate coordinates
            lat, lon = coordinates
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                self.logger.warning(f"Invalid coordinates: {coordinates}")
                return None
                
            result = reverse_geocoder.search([coordinates])[0]
            return {
                'city': result['name'],
                'admin1': result['admin1'],  # State/Province
                'admin2': result['admin2'],  # County/District
                'country': result['cc'],     # Country code
            }
        except Exception as e:
            self.logger.warning(f"Failed to get location info for coordinates {coordinates}: {str(e)}")
            return None

    def format_location_string(self, location_info: Dict) -> str:
        """Format location information into a readable string."""
        if not location_info:
            return "Unknown Location"
            
        components = []
        if location_info.get('city'):
            components.append(location_info['city'])
        if location_info.get('admin1'):
            components.append(location_info['admin1'])
        if location_info.get('country'):
            components.append(location_info['country'])
            
        return ", ".join(components) if components else "Unknown Location"
