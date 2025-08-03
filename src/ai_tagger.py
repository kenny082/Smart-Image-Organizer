from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from typing import List, Optional
import torch
import logging
from pathlib import Path

class AITagger:
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.logger = logging.getLogger(__name__)
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = CLIPModel.from_pretrained(model_name).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.logger.info(f"AI Tagger initialized using {self.device}")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Tagger: {str(e)}")
            raise

    def generate_tags(self, image_path: Path, confidence_threshold: float = 0.5) -> List[str]:
        """
        Generate tags for an image using the CLIP model.
        Args:
            image_path: Path to the image file
            confidence_threshold: Minimum confidence score for tags
        Returns:
            List of generated tags
        """
        try:
            # Predefined categories for classification
            categories = [
                "landscape", "portrait", "wildlife", "urban", "nature",
                "indoor", "outdoor", "day", "night", "sunset",
                "beach", "mountain", "forest", "city", "water",
                "people", "animal", "building", "food", "vehicle",
                "sports", "art", "technology", "abstract", "event"
            ]

            # Load and preprocess the image
            image = Image.open(image_path)
            inputs = self.processor(
                images=image,
                text=categories,
                return_tensors="pt",
                padding=True
            ).to(self.device)

            # Get model outputs
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)[0]

            # Get tags above threshold
            tags = [
                category for category, prob in zip(categories, probs)
                if prob > confidence_threshold
            ]

            return tags

        except Exception as e:
            self.logger.warning(f"Failed to generate tags for {image_path}: {str(e)}")
            return []

    def save_tags(self, image_path: Path, tags: List[str], output_path: Optional[Path] = None) -> None:
        """
        Save generated tags to a file.
        Args:
            image_path: Path to the original image
            tags: List of generated tags
            output_path: Optional path to save tags (defaults to image_path with .json extension)
        """
        import json
        
        try:
            if output_path is None:
                output_path = image_path.with_suffix('.json')
                
            tag_data = {
                'image_path': str(image_path),
                'tags': tags,
                'timestamp': str(datetime.datetime.now())
            }
            
            with open(output_path, 'w') as f:
                json.dump(tag_data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Failed to save tags for {image_path}: {str(e)}")
