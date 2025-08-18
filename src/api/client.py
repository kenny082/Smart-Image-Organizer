"""
Client library for the Image Metadata API.
"""

import requests
from pathlib import Path
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class ImageMetadataClient:
    """Client for interacting with the Image Metadata API."""

    def __init__(
        self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None
    ):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the API
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API key is required")

    def _get_headers(self) -> Dict:
        """Get request headers."""
        return {"X-API-Key": self.api_key}

    def extract_metadata(self, image_path: Path) -> Dict:
        """
        Send an image to the API and get its metadata.

        Args:
            image_path: Path to the image file

        Returns:
            Dict: Image metadata

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        with open(image_path, "rb") as f:
            files = {"file": (image_path.name, f, "image/jpeg")}
            response = requests.post(
                f"{self.base_url}/api/v1/extract-metadata/",
                headers=self._get_headers(),
                files=files,
            )
            response.raise_for_status()
            return response.json()

    def check_health(self) -> Dict:
        """
        Check if the API is healthy.

        Returns:
            Dict: Health check response
        """
        response = requests.get(
            f"{self.base_url}/api/v1/health", headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_rate_limit(self) -> Dict:
        """
        Get current rate limit status.

        Returns:
            Dict: Rate limit information
        """
        response = requests.get(
            f"{self.base_url}/api/v1/rate-limit", headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
