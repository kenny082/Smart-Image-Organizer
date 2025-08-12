import pytest
from pathlib import Path
from src.ai_tagger import AITagger
from PIL import Image
import torch

@pytest.fixture
def sample_image(tmp_path):
    # Create a test image
    img_path = tmp_path / "test.jpg"
    img = Image.new('RGB', (224, 224), color='red')
    img.save(img_path, 'JPEG')
    return img_path

@pytest.fixture
def ai_tagger():
    return AITagger()

def test_ai_tagger_initialization(ai_tagger):
    """Test AI Tagger initialization"""
    assert ai_tagger.model is not None
    assert ai_tagger.processor is not None
    assert ai_tagger.device in ['cuda', 'cpu']

def test_generate_tags(ai_tagger, sample_image):
    """Test tag generation for a sample image"""
    tags = ai_tagger.generate_tags(sample_image)
    assert isinstance(tags, list)
    # Since it's a red image, it might be tagged as 'abstract' or similar
    assert len(tags) > 0

def test_generate_tags_invalid_image(ai_tagger, tmp_path):
    """Test tag generation with invalid image"""
    invalid_path = tmp_path / "nonexistent.jpg"
    tags = ai_tagger.generate_tags(invalid_path)
    assert isinstance(tags, list)
    assert len(tags) == 0

def test_save_tags(ai_tagger, sample_image, tmp_path):
    """Test saving tags to a file"""
    tags = ["test_tag1", "test_tag2"]
    output_path = tmp_path / "tags.json"
    ai_tagger.save_tags(sample_image, tags, output_path)
    assert output_path.exists()

def test_save_tags_default_path(ai_tagger, sample_image):
    """Test saving tags with default output path"""
    tags = ["test_tag1", "test_tag2"]
    ai_tagger.save_tags(sample_image, tags)
    json_path = Path(sample_image).with_suffix('.json')
    assert json_path.exists()
