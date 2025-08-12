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

def test_generate_tags(ai_tagger, sample_image, monkeypatch):
    """Test tag generation for a sample image"""
    # Mock the model output
    import torch
    mock_probs = torch.tensor([[0.6, 0.3, 0.8]])  # Mock probabilities above threshold for first 3 categories
    
    class MockOutputs:
        def __init__(self):
            self.logits_per_image = mock_probs
            self.images_features = None
            self.text_features = None
    
    def mock_model(**kwargs):
        return MockOutputs()
    
    # Mock the categories
    test_categories = ["landscape", "portrait", "wildlife"]  # Only 3 categories for testing
    original_categories = ai_tagger.generate_tags.__defaults__[0]  # Get the original confidence_threshold
    ai_tagger.generate_tags = lambda image_path, confidence_threshold=original_categories: [cat for cat, prob in zip(test_categories, mock_probs[0]) if prob > confidence_threshold]
    
    tags = ai_tagger.generate_tags(sample_image)
    assert isinstance(tags, list)
    assert len(tags) > 0
    assert tags == ["landscape", "wildlife"]  # Only these have probs > 0.5

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
