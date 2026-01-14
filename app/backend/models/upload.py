from pydantic import BaseModel
from datetime import datetime


class FileUploadResponse(BaseModel):
    """Response model for file upload."""
    filename: str
    file_id: str
    chunks_created: int
    status: str
    message: str = ""

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "document.pdf",
                "file_id": "abc123",
                "chunks_created": 42,
                "status": "success",
                "message": "File processed successfully"
            }
        }


class FileMetadata(BaseModel):
    """Metadata about an uploaded file."""
    file_id: str
    filename: str
    upload_time: datetime
    file_size: int
    chunk_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "abc123",
                "filename": "document.pdf",
                "upload_time": "2026-01-14T10:30:00",
                "file_size": 1024000,
                "chunk_count": 42
            }
        }
