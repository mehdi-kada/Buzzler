from app.models.enums import VideoStatus
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any


class VideoUploadRequest(BaseModel):
    url: HttpUrl
    custom_file_name: Optional[str] = None
    
class VideoUploadResponse(BaseModel):
    task_id: str
    status: VideoStatus
    message: Optional[str] = None
    
class VideoProgressUpdate(BaseModel):
    task_id: str
    status: str  # Changed from VideoStatus to str to avoid serialization issues
    progress_percentage: float
    uploaded_bytes: int
    total_bytes: Optional[int] = None
    current_step: str
    blob_name: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class VideoInfo(BaseModel):
    title: str
    duration: Optional[int] = None
    uploader: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    thumbnail: Optional[str] = None
    description: Optional[str] = None