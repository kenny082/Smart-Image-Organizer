import pytest
from pathlib import Path
from src.exif_handler import ExifHandler
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import piexif
from datetime import datetime


@pytest.fixture
def sample_image_no_exif(tmp_path):
    """Create a test image without EXIF data"""
    img_path = tmp_path / "test_no_exif.jpg"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path, "JPEG")
    return img_path


@pytest.fixture
def sample_image_with_exif(tmp_path):
    """Create a test image with EXIF data including GPS"""
    img_path = tmp_path / "test_with_exif.jpg"
    img = Image.new("RGB", (100, 100), color="blue")

    # Create EXIF data
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Make: "Test Camera",
            piexif.ImageIFD.Model: "Test Model",
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: datetime.now().strftime(
                "%Y:%m:%d %H:%M:%S"
            ),
            piexif.ExifIFD.LensModel: "Test Lens",
            piexif.ExifIFD.FNumber: (28, 10),  # F2.8
            piexif.ExifIFD.ISOSpeedRatings: 100,
        },
        "GPS": {
            piexif.GPSIFD.GPSLatitude: ((40, 1), (44, 1), (0, 1)),
            piexif.GPSIFD.GPSLongitude: ((73, 1), (59, 1), (0, 1)),
            piexif.GPSIFD.GPSLatitudeRef: "N",
            piexif.GPSIFD.GPSLongitudeRef: "W",
        },
    }

    exif_bytes = piexif.dump(exif_dict)
    img.save(img_path, "jpeg", exif=exif_bytes)
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
    assert exif_handler._convert_to_degrees((40, 44, 0)) == 40.73333333333333


def test_get_exif_data_with_exif(exif_handler, sample_image_with_exif):
    """Test extraction of EXIF data from image with EXIF"""
    exif_data = exif_handler.get_exif_data(sample_image_with_exif)
    assert isinstance(exif_data, dict)
    assert len(exif_data) > 0
    assert "Make" in exif_data
    assert "Model" in exif_data
    assert "DateTimeOriginal" in exif_data
    assert "GPSInfo" in exif_data


def test_get_date_taken_with_date(exif_handler, sample_image_with_exif):
    """Test date extraction with date in EXIF"""
    exif_data = exif_handler.get_exif_data(sample_image_with_exif)
    date_taken = exif_handler.get_date_taken(exif_data)
    assert date_taken is not None
    # Verify date format
    datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")


def test_get_gps_coordinates_with_gps(exif_handler, sample_image_with_exif):
    """Test GPS extraction with GPS data present"""
    exif_data = exif_handler.get_exif_data(sample_image_with_exif)
    coords = exif_handler.get_gps_coordinates(exif_data)
    assert coords is not None
    assert len(coords) == 2
    lat, lon = coords
    assert abs(lat - 40.73333333333333) < 0.0001  # approximately 40°44'00"N
    assert abs(lon - -73.98333333333333) < 0.0001  # approximately 73°59'00"W


def test_get_camera_info_with_data(exif_handler, sample_image_with_exif):
    """Test camera info extraction with camera data present"""
    exif_data = exif_handler.get_exif_data(sample_image_with_exif)
    camera_info = exif_handler.get_camera_info(exif_data)
    assert isinstance(camera_info, dict)
    assert len(camera_info) > 0
    assert camera_info.get("make") == "Test Camera"
    assert camera_info.get("model") == "Test Model"
    assert camera_info.get("lens") == "Test Lens"
    assert camera_info.get("f_number") is not None
    assert camera_info.get("iso") == "100"


def test_error_handling_invalid_image(exif_handler, tmp_path):
    """Test handling of invalid image files"""
    invalid_file = tmp_path / "invalid.jpg"
    invalid_file.write_text("This is not an image")
    exif_data = exif_handler.get_exif_data(invalid_file)
    assert isinstance(exif_data, dict)
    assert len(exif_data) == 0


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ((45, 30, 0), 45.5),
        ((40, 44, 0), 40.73333333333333),
        ((0, 0, 0), 0.0),
        ((90, 0, 0), 90.0),
    ],
)
def test_convert_to_degrees_parameterized(exif_handler, test_input, expected):
    """Test GPS coordinate conversion with multiple inputs"""
    assert abs(exif_handler._convert_to_degrees(test_input) - expected) < 0.0001
