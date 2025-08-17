from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from app.models.enums import VideoSource, VideoStatus
from app.services.azure_storage import AzureUploadService
from app.models.video import Video
from app.schemas.schema_upload_video import VideoRequest, VideoUploadCompleteRequest
from app.models.user import User
from app.core.auth.auth_endpoints import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from datetime import datetime, timezone

router = APIRouter()

@router.post("/generate-sas")
async def generate_sas(
    request: VideoRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a SAS URL for uploading a video file to Azure Blob Storage.
    """
    azure_service = AzureUploadService()
    sas_url, file_path = azure_service.generate_sas(request.file_name)
    video = Video(
        user_id=current_user.id,
        source= VideoSource.URL_IMPORT if request.is_url else VideoSource.UPLOAD,
        original_filename=request.file_name,
        azure_file_path=file_path,
        upload_url=sas_url,
        status= VideoStatus.PENDING_UPLOAD,
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)

    return {
        "sas_url": sas_url,
        "file_path": file_path,
        "video_id": video.id
    }

@router.post("/complete")
async def complete_upload(
    request: VideoUploadCompleteRequest,
    video_id: Optional[int] = Query(None, description="Optional video id to identify the record"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark the video upload as complete and update its metadata.
    """
    if video_id is not None:
        stmt = select(Video).where(Video.id == video_id, Video.user_id == current_user.id)
    else:
        stmt = select(Video).where(Video.original_filename == request.file_name, Video.user_id == current_user.id)

    result = await db.execute(stmt)
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.file_size_bytes = request.file_size
    video.azure_video_url = request.azure_blob_url
    video.status = VideoStatus.READY
    video.upload_completed_at = datetime.now(timezone.utc)

    db.add(video)
    await db.commit()
    await db.refresh(video)

    return {"message": "Upload completed successfully", "video_id": video.id}
