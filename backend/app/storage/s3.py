import os
import uuid
from fastapi import HTTPException
from ..config import get_settings

settings = get_settings()

# Directory for local uploads (relative to project root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def _local_path(key: str) -> str:
    # Ensure key does not contain path traversal
    safe_key = os.path.normpath(key).replace("..", "")
    return os.path.join(BASE_DIR, safe_key)

def upload_file_to_s3(file_bytes: bytes, filename: str, content_type: str, user_id: int) -> dict:
    """Store file locally and return a pseudo S3 key and URL.
    The returned URL points to the FastAPI static files mount at /uploads.
    """
    ext = os.path.splitext(filename)[1].lower()
    unique_key = f"users/{user_id}/notes/{uuid.uuid4().hex}{ext}"
    file_path = _local_path(unique_key)
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {e}")
    # Construct URL for static serving
    url = f"/uploads/{unique_key}"
    return {"key": unique_key, "url": url}

def delete_file_from_s3(file_key: str) -> bool:
    """Delete a locally stored file."""
    file_path = _local_path(file_key)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except OSError:
        return False

def generate_presigned_url(file_key: str, expiry: int = 3600) -> str:
    """Generate a URL for local file access. Expiry is ignored for local files."""
    return f"/uploads/{file_key}"

# AWS S3 functionality removed for local development
