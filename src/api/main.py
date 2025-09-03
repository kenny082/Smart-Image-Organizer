"""Main API module for the Image Metadata service.

Implements endpoints for metadata extraction and organization.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ..exif_handler import ExifHandler
from .auth import verify_api_key
from .cache import metadata_cache
from .rate_limiter import rate_limiter

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Image Metadata API",
    description="API for extracting and organizing image metadata",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers
exif_handler = ExifHandler()


@app.post("/api/v1/extract-metadata/")
async def extract_metadata(
    file: UploadFile = File(...), api_key: str = Depends(verify_api_key)
) -> Dict:
    """
    Extract metadata from an uploaded image file.

    Args:
        file: Uploaded image file
        api_key: API key for authentication

    Returns:
        Dict: Extracted metadata

    Raises:
        HTTPException: If file is invalid or processing fails
    """
    # Check rate limit
    await rate_limiter.check(api_key)

    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save temporary file
    temp_path = Path(f"temp_{file.filename}")
    try:
        with temp_path.open("wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Check cache
        cached_metadata = metadata_cache.get(temp_path)
        if cached_metadata:
            return cached_metadata

        # Extract metadata
        exif_data = exif_handler.get_exif_data(temp_path)
        gps_coords = exif_handler.get_gps_coordinates(exif_data)
        camera_info = exif_handler.get_camera_info(exif_data)
        date_taken = exif_handler.get_date_taken(exif_data)

        metadata = {
            "filename": file.filename,
            "date_taken": date_taken,
            "gps_coordinates": gps_coords,
            "camera_info": camera_info,
            "exif_data": exif_data,
            "file_size": temp_path.stat().st_size,
            "content_type": file.content_type,
            "processed_at": datetime.utcnow().isoformat(),
        }

        # Cache the results
        metadata_cache.set(temp_path, metadata)

        return metadata

    finally:
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()


@app.get("/api/v1/health")
async def health_check() -> Dict:
    """
    Health check endpoint.

    Returns:
        Dict: Service health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "cache_stats": metadata_cache.get_stats(),
    }


@app.get("/api/v1/rate-limit")
async def get_rate_limit(api_key: str = Depends(verify_api_key)) -> Dict:
    """
    Get current rate limit status.

    Args:
        api_key: API key for authentication

    Returns:
        Dict: Rate limit information
    """
    remaining = rate_limiter.get_remaining_requests(api_key)
    return {
        "remaining_requests": remaining,
        "limit_per_minute": rate_limiter.requests_per_minute,
    }


def start_api(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the FastAPI server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_api()
