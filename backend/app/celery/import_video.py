import celery
from app.celery.celery_app import celery_app
from app.config import settings
import redis
from typing import Optional

from app.services.video_services import ConcurrentStreamingVideoService, StreamingVideoService
from app.models.enums import VideoStatus
from app.schemas.schema_import_video import VideoProgressUpdate


# global instances for rate limitng 
redis_client = redis.from_url(settings.REDIS_URL)
concurent_uploads = ConcurrentStreamingVideoService(max_concurrent_uploads=5)

@celery_app.task(bind=True, max_retries=3)
def process_video_upload_streaming(self, url:str, format_selector: str, custom_filename: Optional[str] = None): 
    """
        task to upload video from a streaming source (like youtube, vimeo, etc.) directly to azure with no disk space usage
    """
    
    task_id = self.request.id
    streaming_service = StreamingVideoService()
    
    def update_progress(status: VideoStatus, progress_data: dict): 
        """ update task progress in redis  """
        progress_update = VideoProgressUpdate(
            task_id= task_id,
            status= status,
            **progress_data
        )
        
        # store progress in redis with an expiration time of 1 hour
        redis_client.setex(
             f"video_upload_progress:{task_id}",
                3600,
                progress_update.model_dump_json()
        )
        
        #update celery task state
        self.update_state(
            state=status.value,
            meta=progress_update.model_dump()
        )
        
    def progress_callback(info: dict):
        update_progress(VideoStatus.UPLOADING, info)
    
    try:
        # check the server capacity 
        active_uploads = concurent_uploads.get_active_uploads()
        if active_uploads >= concurent_uploads.max_concurrent_uploads:
            update_progress(VideoStatus.PENDING_UPLOAD, {
                            'current_step': 'waiting_for_slot',
                            'progress_percentage': 0,
                            'message': f'Waiting for available slot (currently {active_uploads} active uploads)'
                        })
        # extract video info no download
        update_progress(VideoStatus.UPLOADING, {
            'current_step': 'extracting_video_info',
            'progress_percentage': 2,
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
            'blob_name': final_blob_name,
            'blob_url': blob_url,
            'metadata': video_info,
            'message': 'Video successfully streamed to Azure Blob Storage'
        }

        update_progress(VideoStatus.READY, success_data)

    except Exception as e:
        error_data = {
            'current_step': 'failed',
            'progress_percentage': 0,
            'error_message': str(e),
            'message': f'Upload failed: {str(e)}'
        }
        update_progress(VideoStatus.FAILED, error_data)

        # retry with exponential backoff
        self.retry(exc=e, countdown=2 ** self.request.retries)