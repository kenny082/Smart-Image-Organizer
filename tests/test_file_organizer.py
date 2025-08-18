import pytest
from src.file_organizer import FileOrganizer
import json
import shutil


@pytest.fixture
def sample_dirs(tmp_path):
    # Create source and destination directories
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "destination"
    source_dir.mkdir()
    dest_dir.mkdir()
    return source_dir, dest_dir


@pytest.fixture
def sample_image(sample_dirs):
    # Create a test image in the source directory
    source_dir = sample_dirs[0]
    img_path = source_dir / "test.jpg"
    with open(img_path, "wb") as f:
        f.write(b"dummy image data")
    return img_path


@pytest.fixture
def file_organizer(sample_dirs):
    source_dir, dest_dir = sample_dirs
    return FileOrganizer(source_dir, dest_dir, use_ai=False)


def test_scan_images(file_organizer, sample_image):
    """Test scanning for image files"""
    images = file_organizer.scan_images()
    assert len(images) == 1
    assert images[0].name == "test.jpg"


def test_organize_images_dry_run(file_organizer, sample_image):
    """Test organizing images in dry run mode"""
    stats = file_organizer.organize_images(dry_run=True)
    assert stats["processed"] == 1
    assert stats["moved"] == 1
    assert stats["errors"] == 0
    # Check that no files were actually moved
    assert sample_image.exists()


def test_organize_images_live(file_organizer, sample_image):
    """Test organizing images in live mode"""
    stats = file_organizer.organize_images(dry_run=False)
    assert stats["processed"] == 1
    assert stats["moved"] == 1
    assert stats["errors"] == 0
    # Check that the file was moved
    assert not sample_image.exists()


def test_save_operations_log(file_organizer, tmp_path):
    """Test saving operations log"""
    log_path = tmp_path / "operations.json"
    file_organizer.operations_log = [
        {"source": "test.jpg", "destination": "new/test.jpg"}
    ]
    file_organizer.save_operations_log(log_path)
    assert log_path.exists()
    with open(log_path) as f:
        log_data = json.load(f)
    assert len(log_data) == 1


def test_undo_operations(file_organizer, sample_image, sample_dirs):
    """Test undoing operations"""
    dest_dir = sample_dirs[1]
    # Move a file
    new_location = dest_dir / "test.jpg"
    shutil.move(str(sample_image), str(new_location))

    # Create operations log
    file_organizer.operations_log = [
        {"source": str(sample_image), "destination": str(new_location)}
    ]

    # Undo operations
    file_organizer.undo_operations()

    # Check that file is back in original location
    assert sample_image.exists()
    assert not new_location.exists()
