import subprocess
import base64
import uuid
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Callable, List, cast
import logging
from app.services.azure_storage import AzureUploadService
from yt_dlp import YoutubeDL
import threading

# Set up logging
logger = logging.getLogger(__name__)

class StreamingVideoService:
    """
    Service responsible for extracting video metadata via yt-dlp and streaming
    downloads directly into Azure Blob Storage in block-chunks without using local disk.
    """

    def __init__(self) -> None:
        self.azure_service = AzureUploadService()
        # 4 MiB chunk size; adjust according to Azure limits and memory constraints
        self.chunk_size: int = 4 * 1024 * 1024

    def extract_video_info(self, url: str) -> Dict[str, Any]:
        """
        Extracts basic video information for the given URL without downloading the file.
        """
        if not url:
            return {'url': '', 'title': None, 'duration': None, 'size': None, 'formats': []}

        ydl_opts: Dict[str, Any] = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,  # single-video extraction
        }

        with YoutubeDL(cast(Any, ydl_opts)) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                    'thumbnail': info.get('thumbnail'),
                    'description': (info.get('description') or '')[:500],
                    'id': info.get('id'),
                    'ext': info.get('ext', 'mp4'),
                }
            except Exception as e:
                raise RuntimeError(f"Failed to extract video info: {str(e)}") from e

    def generate_blob_name(self, video_info: Dict[str, Any], custom_file_name: Optional[str] = None) -> str:
        """
        Generate a reasonably unique blob name based on video metadata.
        """
        ext = video_info.get('ext', 'mp4')
        if custom_file_name:
            return f"{custom_file_name}.{ext}"

        title = (video_info.get('title') or 'video').replace(' ', '_')
        unique_id = video_info.get('id') or str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"{title}_{unique_id}_{timestamp}.{ext}"

    def _make_block_id(self, counter: int) -> str:
        # Azure expects base64-encoded block IDs; keep them fixed-width for ordering.
        return base64.b64encode(f"{counter:010d}".encode()).decode()

    def stream_download_to_azure(
        self,
        url: str,
        format_selector: str,
        blob_name: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> str:
        """
        Stream a video from `url` using yt-dlp and upload directly to Azure Blob Storage
        in blocks without writing to local disk.
        """
        if not url or not blob_name:
            raise ValueError("URL and blob name must be provided")

        blob_client = self.azure_service.blob_service.get_blob_client(
            container=self.azure_service.container_name,
            blob=blob_name,
        )

        block_list: List[str] = []
        block_id_counter = 0
        total_uploaded = 0

        MAX_STAGE_RETRIES = 3
        RETRY_BACKOFF = 1.5  # base seconds for exponential backoff

        cmd = [
            "yt-dlp",
            "--format",
            format_selector,
            "--output",
            "-",  # stdout
            "--quiet",
            "--no-warnings",
            url,
        ]

        process = None
        try:
            if progress_callback:
                progress_callback({"current_step": "starting_download", "progress_percentage": 5})

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

            if progress_callback:
                progress_callback({"current_step": "streaming_to_azure", "progress_percentage": 10})

            if process.stdout is None:
                raise RuntimeError("yt-dlp subprocess stdout unavailable")

            while True:
                chunk = process.stdout.read(self.chunk_size)
                if not chunk:
                    break

                block_id = self._make_block_id(block_id_counter)

                # Try to stage the block with a small retry loop for transient failures.
                for attempt in range(1, MAX_STAGE_RETRIES + 1):
                    try:
                        # stage_block typically accepts (block_id, data)
                        blob_client.stage_block(block_id, chunk)
                        break
                    except Exception as e:
                        if attempt < MAX_STAGE_RETRIES:
                            time.sleep(RETRY_BACKOFF ** (attempt - 1))
                            continue
                        else:
                            # stop the child process and re-raise with context
                            try:
                                if process:
                                    process.terminate()
                                    process.wait(timeout=5)
                            except Exception:
                                pass
                            raise RuntimeError(f"Failed to upload chunk to Azure after retries: {str(e)}") from e

                block_list.append(block_id)
                block_id_counter += 1
                total_uploaded += len(chunk)

                if progress_callback:
                    # Heuristic progress (we don't know total size)
                    estimated_progress = min(10 + (total_uploaded / (1024 * 1024)) * 2, 95)
                    progress_callback(
                        {
                            "current_step": "uploading_to_azure",
                            "progress_percentage": estimated_progress,
                            "uploaded_bytes": total_uploaded,
                            "chunk_size": len(chunk),
                        }
                    )

            # Wait for yt-dlp to finish and ensure it exited successfully
            if process is None:
                raise RuntimeError("yt-dlp process was not started as expected")

            # Read any error output from yt-dlp
            stderr_output = b""
            if process.stderr:
                stderr_output = process.stderr.read()
                
            return_code = process.wait()
            if return_code != 0:
                error_msg = stderr_output.decode() if stderr_output else f"yt-dlp failed with return code {return_code}"
                raise RuntimeError(f"yt-dlp failed: {error_msg}")

            if block_list:
                blob_client.commit_block_list(cast(List[Any], block_list))

                if progress_callback:
                    progress_callback(
                        {
                            "current_step": "completed",
                            "progress_percentage": 100,
                            "uploaded_bytes": total_uploaded,
                            "total_bytes": total_uploaded,
                        }
                    )
            else:
                raise RuntimeError("No data was downloaded from the video")

            return blob_name

        except Exception as exc:
            # Attempt to remove any partially uploaded blob
            try:
                blob_client.delete_blob()
            except Exception:
                # ignore deletion errors, nothing we can do here
                pass
            raise RuntimeError(f"Streaming upload failed: {str(exc)}") from exc

        finally:
            # Ensure the subprocess is terminated
            if process is not None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        process.kill()
                        process.wait(timeout=5)
                    except Exception:
                        pass
                except Exception:
                    try:
                        process.kill()
                    except Exception:
                        pass



class ConcurrentStreamingVideoService:
    """
    Manages multiple concurrent streaming uploads to Azure Blob Storage.
    Limits the number of simultaneous uploads to avoid overwhelming resources.
    """
    def __init__(self, max_concurrent_uploads: int = 5):
        self.max_concurrent_uploads = max_concurrent_uploads
        self.active_uploads = {}
        self.upload_semaphore = threading.Semaphore(max_concurrent_uploads)

    def stream_with_concurrency_limit(
        self,
        task_id: str,
        url: str,
        format_selector: str,
        blob_name: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> str:
        """
        Stream a video with concurrency control.
        """
        if not url or not blob_name:
            raise ValueError("URL and blob name must be provided")

        # wrapper to add task_id to progress info
        def progress_wrapper(info):
            callback_info = dict(info) if isinstance(info, dict) else {'info': info}
            callback_info['task_id'] = task_id
            if progress_callback:
                progress_callback(callback_info)

        if not self.upload_semaphore.acquire(blocking=False):
            # If we can't acquire the semaphore immediately, raise an exception
            raise RuntimeError("Server is at maximum concurrent upload capacity")

        try:
            self.active_uploads[task_id] = {
                'status': "processing",
                'start_time': datetime.utcnow(),
            }

            streaming_service = StreamingVideoService()
            result = streaming_service.stream_download_to_azure(
                url, format_selector, blob_name, progress_wrapper if progress_callback else None
            )

            self.active_uploads[task_id]['status'] = "completed"

            return result
        except Exception as e:
            self.active_uploads[task_id]['status'] = "failed"
            raise e
        finally:
            self.upload_semaphore.release()
            if task_id in self.active_uploads:
                del self.active_uploads[task_id]


    def get_active_uploads(self) -> int:
        return len([u for u in self.active_uploads.values() if u['status'] == 'processing'])

    def cleanup_old_uploads(self, max_age_hours: int = 24):
        """Clean up old upload records."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        self.active_uploads = {
            k: v for k, v in self.active_uploads.items()
            if v['start_time'] > cutoff
        }
