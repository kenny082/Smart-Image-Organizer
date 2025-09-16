import datetime
import logging
import os
from os import PathLike
from pathlib import Path
from typing import List, Optional, Union

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


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

    def generate_tags(
        self, image_path: Union[str, PathLike[str]], confidence_threshold: float = 0.5
    ) -> List[str]:
        """
        Generate tags for an image using the CLIP model.
        Args:
            image_path: Path to the image file (can be string or Path)
            confidence_threshold: Minimum confidence score for tags
        Returns:
            List of generated tags
        """
        try:
            # Predefined categories for classification
            categories = [
                "landscape",
                "portrait",
                "wildlife",
                "urban",
                "nature",
                "indoor",
                "outdoor",
                "day",
                "night",
                "sunset",
                "beach",
                "mountain",
                "forest",
                "city",
                "water",
                "people",
                "animal",
                "building",
                "food",
                "vehicle",
                "sports",
                "art",
                "technology",
                "abstract",
                "event",
            ]

            # Load and preprocess the image
            image = Image.open(os.fspath(image_path))
            inputs = self.processor(
                images=image, text=categories, return_tensors="pt", padding=True
            ).to(self.device)

            # Get model outputs
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)[0]

            # Get tags above threshold
            tags = []
            for category, prob in zip(categories, probs):
                if prob > confidence_threshold:
                    tags.append(category)

            return tags

        except Exception as e:
            self.logger.warning(f"Failed to generate tags for {image_path}: {str(e)}")
            return []

    def save_tags(
        self,
        image_path: Union[str, PathLike[str]],
        tags: List[str],
        output_path: Optional[Union[str, PathLike[str]]] = None,
    ) -> None:
        """
        Save generated tags to a file.
        Args:
            image_path: Path to the original image (can be string or Path)
            tags: List of generated tags
            output_path: Optional path for saving tags (defaults to .json)
        """
        import json

        try:
            image_path = Path(os.fspath(image_path))
            if output_path is None:
                output_path = image_path.with_suffix(".json")
            else:
                output_path = Path(os.fspath(output_path))

            tag_data = {
                "image_path": str(image_path),
                "tags": tags,
                "timestamp": str(datetime.datetime.now()),
            }

            with open(output_path, "w") as f:
                json.dump(tag_data, f, indent=2)

        except Exception as e:
            self.logger.warning(f"Failed to save tags for {image_path}: {str(e)}")
