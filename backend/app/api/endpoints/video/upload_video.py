from fastapi import APIRouter, Depends
from backend.app.models.enums import VideoSource, VideoStatus
from app.services.azure_storage import AzureUploadService
from app.models.video import Video
from app.schemas.schema_upload_video import VideoRequest, VideoUploadCompleteRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from datetime import datetime, timezone

router = APIRouter(prefix="/upload", tags=["video"])

@router.post("/generate-sas")
async def generate_sas(request: VideoRequest, db: AsyncSession = Depends(get_db)):
    """
    Generate a SAS URL for uploading a video file to Azure Blob Storage.
    """
    azure_service = AzureUploadService()
    sas_url, file_path = azure_service.generate_sas(request.file_name)
    video = Video(
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
async def complete_upload(request: VideoUploadCompleteRequest, db: AsyncSession = Depends(get_db)):
    """
    Mark the video upload as complete and update its metadata.
    """
    stmt = select(Video).where(Video.original_filename == request.file_name)
    result = await db.execute(stmt)
    video = result.scalar_one_or_none()
    if not video:
        return {"error": "Video not found"}

    video.file_size_bytes = request.file_size
    video.azure_video_url = request.azure_blob_url
    video.status = VideoStatus.READY
    video.upload_completed_at = datetime.now(timezone.utc)

    db.add(video)
    await db.commit()
    await db.refresh(video)

    return {"message": "Upload completed successfully", "video_id": video.id}
