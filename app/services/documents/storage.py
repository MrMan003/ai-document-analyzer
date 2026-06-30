"""
File storage abstraction layer.
"""
import os
import shutil
import hashlib
from typing import Optional, BinaryIO
from pathlib import Path
from datetime import datetime  # Add this import

from app.core.config import settings


class StorageService:
    """File storage service supporting local, S3, and Azure Blob."""

    def __init__(self):
        self.backend = settings.STORAGE_BACKEND
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, file_content: bytes, filename: str) -> tuple[str, int]:
        """Save a file and return (storage_path, file_size)."""
        # Generate unique filename
        ext = os.path.splitext(filename)[1] or ".pdf"
        file_hash = hashlib.sha256(file_content).hexdigest()[:16]
        stored_name = f"{file_hash}_{int(datetime.utcnow().timestamp())}{ext}"
        storage_path = self.upload_dir / stored_name

        # Save file
        with open(storage_path, "wb") as f:
            f.write(file_content)

        return str(storage_path), len(file_content)

    def save_upload_file(self, upload_file, filename: str) -> tuple[str, int]:
        """Save an uploaded file."""
        content = upload_file.file.read()
        return self.save_file(content, filename)

    def get_file_path(self, storage_path: str) -> Optional[Path]:
        """Get the full path to a stored file."""
        path = Path(storage_path)
        if path.exists():
            return path
        return None

    def delete_file(self, storage_path: str) -> bool:
        """Delete a file from storage."""
        path = Path(storage_path)
        if path.exists():
            path.unlink()
            return True
        return False

    def get_file_size(self, storage_path: str) -> int:
        """Get file size in bytes."""
        path = Path(storage_path)
        if path.exists():
            return path.stat().st_size
        return 0

    def get_file_hash(self, file_content: bytes) -> str:
        """Get SHA-256 hash of file content."""
        return hashlib.sha256(file_content).hexdigest()


storage_service = StorageService()