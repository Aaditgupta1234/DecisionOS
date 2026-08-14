"""Dataset file storage manager."""

import os
import shutil
import uuid
from typing import Optional, Tuple
from fastapi import HTTPException, UploadFile, status
from app.core.config import settings
from app.core.logging import logger


class DatasetStorage:
    """Handles secure file persistence, unique naming, and storage management for uploaded datasets."""

    def __init__(self, base_dir: Optional[str] = None):
        self.upload_dir = os.path.abspath(base_dir or settings.UPLOAD_DIR)
        os.makedirs(self.upload_dir, exist_ok=True)

    def generate_stored_filename(self, original_filename: str) -> str:
        """Generates a UUID-prefixed unique filename."""
        safe_name = os.path.basename(original_filename).replace(" ", "_")
        return f"{uuid.uuid4().hex[:12]}_{safe_name}"

    def save_upload_file(self, upload_file: UploadFile) -> Tuple[str, str, int]:
        """Saves an incoming UploadFile to local storage.
        
        Returns:
            Tuple of (stored_filename, absolute_file_path, file_size_bytes)
        """
        stored_filename = self.generate_stored_filename(upload_file.filename or "dataset.csv")
        file_path = os.path.join(self.upload_dir, stored_filename)

        total_bytes = 0
        try:
            with open(file_path, "wb") as buffer:
                # Read in 1MB chunks to handle large files efficiently
                while chunk := upload_file.file.read(1024 * 1024):
                    total_bytes += len(chunk)
                    if total_bytes > settings.MAX_UPLOAD_SIZE_BYTES:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB.",
                        )
                    buffer.write(chunk)
            
            # Reset file pointer
            upload_file.file.seek(0)
            return stored_filename, file_path, total_bytes
        except Exception as e:
            self.delete_file(file_path)
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Failed to save upload file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save uploaded file to disk: {str(e)}",
            )

    def delete_file(self, file_path: str) -> bool:
        """Safely removes a file from disk."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            logger.warning(f"Could not delete file {file_path}: {e}")
        return False


storage = DatasetStorage()
