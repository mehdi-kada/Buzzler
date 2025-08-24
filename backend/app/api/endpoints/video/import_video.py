from typing import Optional
from fastapi import APIRouter, HTTPException,status
from app.celery.import_tasks import get_server_stats, process_video_upload_streaming, redis_client
from app.models.enums import VideoStatus
from app.schemas.schema_import_video import VideoProgressUpdate, VideoUploadResponse


router = APIRouter(prefix="/import")


@router.post("/import-video", response_model=VideoUploadResponse)
async def import_video(url: str, format_selector: str, custom_filename: Optional[str] = None):
    """
        orchestrates celery to import video directly to azure
    """
    try:
        task = process_video_upload_streaming.delay(url, format_selector, custom_filename)

        return VideoUploadResponse(
        task_id=task.id,
        status=VideoStatus.UPLOADING,
        message="Video import has been initiated."
    )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start video streaming: {str(e)}"
        )

@router.get("/server-stats")
async def get_import_status():
    """
        checks the stats of the server (number of empty slots, number of active tasks, etc.)
    """
    try:
        stats = get_server_stats.delay()
        result = stats.get(timeout=5)
        return {"server_stats": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get import status: {str(e)}"
        )

@router.get("/task-status/{task_id}", response_model=VideoProgressUpdate)
async def get_task_status(task_id: str):
    """
        get the status of a specific task by its id
    """
    try:
        # try to get the status from redis
        progress_data = await redis_client.get(f"video_upload_progress:{task_id}")

        # try to get it from celery task as a fallback
        if not progress_data:
            task_result = process_video_upload_streaming.AsyncResult(task_id)

            if task_result.state == "PENDING":
                return VideoProgressUpdate(
                    task_id=task_id,
                    status=VideoStatus.PENDING_UPLOAD,
                    progress_percentage=0,
                    uploaded_bytes=0,
                    current_step="queued",
                )
            elif task_result.state == "FAILURE":
                return VideoProgressUpdate(
                    task_id=task_id,
                    status=VideoStatus.FAILED,
                    progress_percentage=0,
                    uploaded_bytes=0,
                    current_step="failed",
                    error_message=str(task_result.info)
                )
            else:
                # For other states, return a generic response
                return VideoProgressUpdate(
                    task_id=task_id,
                    status=VideoStatus.UPLOADING,
                    progress_percentage=0,
                    uploaded_bytes=0,
                    current_step=task_result.state.lower(),
                )

        # Parse progress data from Redis
        try:
            progress_update = VideoProgressUpdate.model_validate_json(progress_data)
            return progress_update
        except Exception:
            # If we can't parse the progress data, fall back to celery task state
            task_result = process_video_upload_streaming.AsyncResult(task_id)
            return VideoProgressUpdate(
                task_id=task_id,
                status=VideoStatus.UPLOADING,
                progress_percentage=0,
                uploaded_bytes=0,
                current_step=task_result.state.lower(),
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress: {str(e)}"
        )
