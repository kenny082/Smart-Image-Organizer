import pytest
from pathlib import Path
from src.geolocation import GeoLocationHandler

@pytest.fixture
def geo_handler():
    return GeoLocationHandler()

def test_get_location_info_valid_coordinates(geo_handler):
    """Test location info retrieval with valid coordinates"""
    # New York City coordinates
    coords = (40.7128, -74.0060)
    location = geo_handler.get_location_info(coords)
    assert location is not None
    assert isinstance(location, dict)
    assert 'city' in location
    assert 'country' in location

def test_get_location_info_invalid_coordinates(geo_handler):
    """Test location info retrieval with invalid coordinates"""
    coords = (200, 200)  # Invalid coordinates
    location = geo_handler.get_location_info(coords)
    assert location is None

def test_format_location_string_full_info(geo_handler):
    """Test location string formatting with complete info"""
    location_info = {
        'city': 'New York',
        'admin1': 'New York',
        'country': 'US'
    }
    result = geo_handler.format_location_string(location_info)
    assert result == "New York, New York, US"

def test_format_location_string_partial_info(geo_handler):
    """Test location string formatting with partial info"""
    location_info = {
        'city': 'New York',
        'country': 'US'
    }
    result = geo_handler.format_location_string(location_info)
    assert result == "New York, US"

def test_format_location_string_no_info(geo_handler):
    """Test location string formatting with no info"""
    result = geo_handler.format_location_string(None)
    assert result == "Unknown Location"
