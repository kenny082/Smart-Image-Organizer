import pytest
from typer.testing import CliRunner
from src.cli import app
from PIL import Image
import json


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_image(tmp_path):
    """Create a test image file."""
    img_path = tmp_path / "test.jpg"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return img_path


@pytest.fixture
def source_dir(tmp_path, sample_image):
    """Create a source directory with a test image."""
    source = tmp_path / "source"
    source.mkdir()
    sample_image.rename(source / "test.jpg")
    return source


@pytest.fixture
def dest_dir(tmp_path):
    """Create a destination directory."""
    dest = tmp_path / "dest"
    dest.mkdir()
    return dest


@pytest.fixture
def log_file(tmp_path):
    """Create a sample operations log."""
    log_path = tmp_path / "operations.json"
    operations = [
        {
            "source": str(tmp_path / "source/test.jpg"),
            "destination": str(tmp_path / "dest/2023/08/Unknown_Location/test.jpg"),
            "date_taken": None,
            "location": None,
            "tags": None,
        }
    ]
    log_path.write_text(json.dumps(operations))
    return log_path


def test_preview_with_valid_directory(runner, source_dir, dest_dir):
    """Test preview command with valid source directory."""
    result = runner.invoke(app, ["preview", str(source_dir), str(dest_dir)])
    assert result.exit_code == 0
    assert "PREVIEW MODE" in result.stdout
    assert "Found 1 images to organize" in result.stdout


def test_preview_with_nonexistent_directory(runner, dest_dir):
    """Test preview command with non-existent source directory."""
    result = runner.invoke(app, ["preview", "/nonexistent", str(dest_dir)])
    assert result.exit_code == 1
    assert "Error: Source directory does not exist" in result.stdout


def test_preview_with_empty_directory(runner, tmp_path, dest_dir):
    """Test preview command with empty source directory."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    result = runner.invoke(app, ["preview", str(empty_dir), str(dest_dir)])
    assert result.exit_code == 1
    assert "No image files found" in result.stdout


def test_organize_dry_run(runner, source_dir, dest_dir):
    """Test organize command in dry run mode."""
    result = runner.invoke(app, ["organize", str(source_dir), str(dest_dir)])
    assert result.exit_code == 0
    assert "DRY RUN" in result.stdout
    # Check that no files were actually moved
    assert len(list(dest_dir.rglob("*"))) == 0


def test_organize_live_run(runner, source_dir, dest_dir):
    """Test organize command in live mode."""
    result = runner.invoke(
        app, ["organize", str(source_dir), str(dest_dir), "--no-dry-run"]
    )
    assert result.exit_code == 0
    assert "LIVE RUN" in result.stdout
    # Check that files were moved
    assert len(list(source_dir.rglob("*.jpg"))) == 0
    assert len(list(dest_dir.rglob("*.jpg"))) == 1


def test_organize_with_ai_tagging(runner, source_dir, dest_dir):
    """Test organize command with AI tagging enabled."""
    result = runner.invoke(
        app, ["organize", str(source_dir), str(dest_dir), "--use-ai"]
    )
    assert result.exit_code == 0
    assert "Images Tagged" in result.stdout


def test_organize_with_log(runner, source_dir, dest_dir, tmp_path):
    """Test organize command with log file."""
    log_path = tmp_path / "test.log"
    result = runner.invoke(
        app, ["organize", str(source_dir), str(dest_dir), "--log", str(log_path)]
    )
    assert result.exit_code == 0
    assert log_path.exists()


def test_undo_with_valid_log(runner, log_file):
    """Test undo command with valid log file."""
    result = runner.invoke(app, ["undo", str(log_file)], input="y\n")
    assert result.exit_code == 0
    assert "Successfully undone all operations" in result.stdout


def test_undo_with_nonexistent_log(runner, tmp_path):
    """Test undo command with non-existent log file."""
    nonexistent = tmp_path / "nonexistent.json"
    result = runner.invoke(app, ["undo", str(nonexistent)])
    assert result.exit_code == 1
    assert "Log file not found" in result.stdout


def test_undo_user_abort(runner, log_file):
    """Test undo command when user aborts."""
    result = runner.invoke(app, ["undo", str(log_file)], input="n\n")
    assert result.exit_code == 0
    assert "Operation aborted by user" in result.stdout
