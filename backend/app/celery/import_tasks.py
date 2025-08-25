from app.celery.celery_app import celery_app
from app.config import settings
import redis
from typing import Optional

from app.services.video_services import ConcurrentStreamingVideoService, StreamingVideoService
from app.models.enums import VideoStatus
from app.schemas.schema_import_video import VideoProgressUpdate

# global instances for rate limiting (sync redis with decoded string responses)
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
concurent_uploads = ConcurrentStreamingVideoService(max_concurrent_uploads=5)

@celery_app.task(bind=True, max_retries=3)
def process_video_upload_streaming(self, url:str, format_selector: str, custom_filename: Optional[str] = None): 
    """
        task to upload video from a streaming source (like youtube, vimeo, etc.) directly to azure with no disk space usage
    """
    
    task_id = self.request.id
    streaming_service = StreamingVideoService()
    
    def update_progress(status: str, progress_data: dict): 
        """ update task progress in redis  """
        # Remove any keys that conflict with explicit parameters
        progress_data_clean = progress_data.copy()
        conflicting_keys = ['task_id', 'status']
        for key in conflicting_keys:
            progress_data_clean.pop(key, None)
            
        progress_update = VideoProgressUpdate(
            task_id= task_id,
            status= status,  # Now status is already a string
            **progress_data_clean
        )
        
        try:
            # store progress in redis with an expiration time of 1 hour
            redis_client.setex(
                f"video_upload_progress:{task_id}",
                3600,
                progress_update.model_dump_json()
            )
        except Exception as e:
            # Log error but don't fail the task because of Redis issues
            pass
        
        #update celery task state
        self.update_state(
            state=status,  # status is already a string
            meta=progress_update.model_dump()
        )
        
    def progress_callback(info: dict):
        # Ensure uploaded_bytes is always present
        if 'uploaded_bytes' not in info:
            info['uploaded_bytes'] = 0
        # Remove task_id from info to avoid conflicts
        info_copy = info.copy()
        info_copy.pop('task_id', None)
        update_progress(VideoStatus.UPLOADING.value, info_copy)  # Use the string value
    
    try:
        # check the server capacity 
        active_uploads = concurent_uploads.get_active_uploads()
        if active_uploads >= concurent_uploads.max_concurrent_uploads:
            update_progress(VideoStatus.PENDING_UPLOAD.value, {
                            'current_step': 'waiting_for_slot',
                            'progress_percentage': 0,
                            'uploaded_bytes': 0,
                            'message': f'Waiting for available slot (currently {active_uploads} active uploads)'
                        })
        # extract video info no download
        update_progress(VideoStatus.UPLOADING.value, {
            'current_step': 'extracting_video_info',
            'progress_percentage': 2,
            'uploaded_bytes': 0,
            'message': 'Extracting video information'
        })
        
        video_info = streaming_service.extract_video_info(url)
        blob_name = streaming_service.generate_blob_name(video_info, custom_filename)
        
        final_blob_name = concurent_uploads.stream_with_concurrency_limit(
            task_id=task_id,
            url=url,
            blob_name=blob_name,
            format_selector=format_selector,
            progress_callback=progress_callback,
        )

        blob_url = streaming_service.azure_service.get_blob_url(final_blob_name)
        
        success_data = {
            'current_step': 'completed',
            'progress_percentage': 100,
            'uploaded_bytes': 0,  # This will be updated by the streaming process
            'blob_name': final_blob_name,
            'blob_url': blob_url,
            'metadata': video_info,
            'message': 'Video successfully streamed to Azure Blob Storage'
        }

        update_progress(VideoStatus.READY.value, success_data)

    except Exception as e:
        error_data = {
            'current_step': 'failed',
            'progress_percentage': 0,
            'uploaded_bytes': 0,
            'error_message': str(e),
            'message': f'Upload failed: {str(e)}',
            'total_bytes': None,
            'blob_name': None,
            'metadata': None
        }
        update_progress(VideoStatus.FAILED.value, error_data)

        # retry with exponential backoff
        self.retry(exc=e, countdown=2 ** self.request.retries)
        
@celery_app.task
def get_server_stats():
    """
    Get the current server statistics.
    """
    try:
        active_uploads = concurent_uploads.get_active_uploads()
        return{
            "active_uploads": active_uploads,
            "active_tasks": active_uploads,  # alias for clients/tests
            "max_concurrent_uploads": concurent_uploads.max_concurrent_uploads,
            "available_slots": concurent_uploads.max_concurrent_uploads - active_uploads
        }
    except Exception as e:
        return {
            "active_uploads": 0,
            "max_concurrent_uploads": 5,
            "available_slots": 5,
            "error": str(e)
        }