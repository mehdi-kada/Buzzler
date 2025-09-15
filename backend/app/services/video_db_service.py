from typing import Any, Optional
from app.db.database import SessionLocal
from app.models.video import Video
from app.models.enums import VideoStatus, VideoSource  # Import if needed

def add_video_info_to_db(
    user_id: str,
    custom_filename: Optional[str] = None,
    video_metadata: Optional[dict[str, Any]] = None
) -> Video:
    db = SessionLocal()
    try:
        metadata = video_metadata or {}
        video = Video(
            user_id=int(user_id),
            source=VideoSource.URL_IMPORT, 
            original_filename=custom_filename or metadata.get('original_filename', 'Unknown'),
            duration_seconds=metadata.get('duration_seconds'),
            file_size_bytes=metadata.get('file_size_bytes'),
            file_extension=metadata.get('file_extension'),
            azure_file_path=metadata.get('azure_file_path'),
            azure_video_url=metadata.get('azure_video_url'),
            status=metadata.get('status', VideoStatus.PENDING_UPLOAD)
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return video
    finally:
        db.close()