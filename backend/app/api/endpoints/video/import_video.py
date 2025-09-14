from typing import Optional
import asyncio
from fastapi import APIRouter, HTTPException, status, Body, Depends
from app.celery.import_tasks import get_server_stats, process_video_upload_streaming, redis_client
from app.models.enums import VideoStatus
from app.schemas.schema_import_video import VideoProgressUpdate, VideoUploadResponse, VideoUploadRequest
from app.core.auth.auth_endpoints import get_current_user
from app.models.user import User


router = APIRouter(prefix="/import")


@router.post("/import-video", response_model=VideoUploadResponse)
async def import_video(video_request: VideoUploadRequest, user: User = Depends(get_current_user)):
    """
        orchestrates celery to import video directly to azure
    """
    url = str(video_request.url)  # Convert HttpUrl to string
    custom_filename = video_request.custom_file_name
    
    try:
        print("the task is about to start : ")
        task = process_video_upload_streaming.delay(url, custom_filename, user.id)
        print(f"the task is : {task}")
        print(f"task id: {task.id}")
        return VideoUploadResponse(
            task_id=task.id,
            status=VideoStatus.UPLOADING,
            message="Video import has been initiated."
        )
    except Exception as e:
        print(f"Failed to start video streaming: {str(e)}")
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
        # fire-and-wait for a short time without blocking the event loop
        async_result = get_server_stats.delay()
        print(f"stats task is : {async_result}")
        print(f"stats task id: {async_result.id}")

        try:
            # run the blocking .get in a thread with a small timeout
            result = await asyncio.wait_for(
                asyncio.to_thread(async_result.get, timeout=2),
                timeout=3,
            )
            print(f"result is : {result}")
            return {"server_stats": result}
        except asyncio.TimeoutError:
            # worker didn't respond in time; return a lightweight in-progress response
            print(f"Timeout getting server stats, task state: {async_result.state}")
            return {
                "task_id": async_result.id,
                "state": async_result.state,
                "message": "server stats are still being gathered; try again shortly",
            }
        except Exception as e:
            # Any other exception (including Celery backend errors) — return a helpful payload
            print(f"Error getting server stats: {e}")
            return {
                "task_id": async_result.id,
                "state": getattr(async_result, "state", "UNKNOWN"),
                "error": str(e),
            }
    except Exception as e:
        print(f"Failed to get import status: {str(e)}")
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
        print(f"Getting task status for task_id: {task_id}")
        # try to get the status from redis with a short timeout so we don't hang
        try:
            # sync redis client call offloaded to thread + timeout
            progress_data = await asyncio.wait_for(
                asyncio.to_thread(redis_client.get, f"video_upload_progress:{task_id}"),
                timeout=2,
            )
            print(f"progress data from redis: {progress_data}")
        except asyncio.TimeoutError:
            print(f"Timeout when getting progress data from redis for task_id: {task_id}")
            progress_data = None
        except Exception as e:
            print(f"Error when getting progress data from redis for task_id: {task_id}, error: {e}")
            progress_data = None

        # try to get it from celery task as a fallback
        if not progress_data:
            print("falling back to celery for task progress")
            task_result = process_video_upload_streaming.AsyncResult(task_id)
            print(f"Celery task result state: {task_result.state}")

            if task_result.state == "PENDING":
                print(f"Task {task_id} is still pending - this might mean no worker is available to process it")
                return VideoProgressUpdate(
                    task_id=task_id,
                    status=VideoStatus.PENDING_UPLOAD,
                    progress_percentage=0,
                    uploaded_bytes=0,
                    current_step="queued",
                )
            elif task_result.state == "FAILURE":
                print(f"Task {task_id} failed with error: {task_result.info}")
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
                print(f"Task {task_id} is in state: {task_result.state}")
                return VideoProgressUpdate(
                    task_id=task_id,
                    status=VideoStatus.UPLOADING,
                    progress_percentage=0,
                    uploaded_bytes=0,
                    current_step=task_result.state.lower(),
                )

        # Parse progress data from Redis
        try:
            # redis returns bytes when using redis-py; ensure we have a str
            if isinstance(progress_data, (bytes, bytearray)):
                progress_data = progress_data.decode("utf-8")

            # ensure it's a plain string for pydantic's model_validate_json
            progress_update = VideoProgressUpdate.model_validate_json(str(progress_data))
            print(f"Successfully parsed progress data from redis: {progress_update}")
            return progress_update
        except Exception as e:
            print(f"Failed to parse progress data from redis: {e}")
            # If we can't parse the progress data, fall back to celery task state
            task_result = process_video_upload_streaming.AsyncResult(task_id)

            # avoid blocking event loop if someone stored a very large state; just read its state
            return VideoProgressUpdate(
                task_id=task_id,
                status=VideoStatus.UPLOADING,
                progress_percentage=0,
                uploaded_bytes=0,
                current_step=(task_result.state or "unknown").lower(),
            )

    except Exception as e:
        print(f"Failed to get progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress: {str(e)}"
        )
