import pytest
from pathlib import Path
from src.exif_handler import ExifHandler
from PIL import Image
import os

@pytest.fixture
def sample_image(tmp_path):
    # Create a test image with EXIF data
    img_path = tmp_path / "test.jpg"
    img = Image.new('RGB', (100, 100), color='red')
    img.save(img_path, 'JPEG')
    return img_path

@pytest.fixture
def exif_handler():
    return ExifHandler()

def test_get_exif_data_no_exif(exif_handler, sample_image):
    """Test handling of images without EXIF data"""
    exif_data = exif_handler.get_exif_data(sample_image)
    assert isinstance(exif_data, dict)
    assert len(exif_data) == 0

def test_get_date_taken_no_date(exif_handler):
    """Test date extraction with no date in EXIF"""
    assert exif_handler.get_date_taken({}) is None

def test_get_gps_coordinates_no_gps(exif_handler):
    """Test GPS extraction with no GPS data"""
    assert exif_handler.get_gps_coordinates({}) is None

def test_get_camera_info_no_info(exif_handler):
    """Test camera info extraction with no camera data"""
    camera_info = exif_handler.get_camera_info({})
    assert isinstance(camera_info, dict)
    assert len(camera_info) == 0

def test_convert_to_degrees(exif_handler):
    """Test GPS coordinate conversion"""
    assert exif_handler._convert_to_degrees((45, 30, 0)) == 45.5
