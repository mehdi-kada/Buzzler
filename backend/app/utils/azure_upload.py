
import time
from typing import Optional, Callable
import logging
from pathlib import Path
from azure.storage.blob.aio import BlobServiceClient
from backend.app.config import Settings


logger = logging.getLogger(__name__)

class AzureStorageError(Exception):
    pass

class AzureUploadProgress:
    def __init__(self, total_size: int, callback: Optional[Callable] = None):
        self.total_size = total_size
        self.callback = callback
        self.start_time = time.time()
        self.uploaded_size = 0

    def update(self, bytes_uploaded: int):
        self.uploaded_size += bytes_uploaded
        progress = (self.uploaded_size / self.total_size) * 100
        if self.callback:
            elapsed_time = time.time() - self.start_time
            speed_mbps = (self.uploaded_size / elapsed_time) / (1024 * 1024) if elapsed_time > 0 else 0
            self.callback({
                'uploaded_bytes': self.uploaded_size,
                'total_bytes': self.total_size,
                'progress_percent': round(progress, 1),
                'speed_mbps': round(speed_mbps, 2),
                'elapsed_seconds': round(elapsed_time, 1)
            })

async def upload_file_to_azure(local_path: Path, azure_path: str, progress_callback: Optional[Callable] = None):
    if not local_path.exists():
        raise AzureStorageError(f"Local file {local_path} does not exist.")

    if not Settings.AZURE_STORAGE_CONNECTION_STRING:
        raise AzureStorageError("Azure Storage connection string is not set.")

    file_size = local_path.stat().st_size
    progress = AzureUploadProgress(file_size, progress_callback)

    logger.info(f"Starting Azure upload: {local_path} -> {azure_path} ({file_size} bytes)")

    try:
        async with BlobServiceClient.from_connection_string(Settings.AZURE_STORAGE_CONNECTION_STRING) as blob_service_client:
            blob_client = blob_service_client.get_blob_client(
                container=Settings.AZURE_CONTAINER_NAME,
                blob=azure_path
            )

            CHUNK_SIZE = 4 * 1024 * 1024  # 4MB chunks
            with open(local_path, 'rb') as file_data:
                block_ids = []
                chunk_number = 0
                while True:
                    chunk = file_data.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    block_id = f"block-{chunk_number:06d}"
                    block_ids.append(block_id)
                    await blob_client.stage_block(
                        block_id=block_id,
                        data=chunk
                    )
                    progress.update(len(chunk))
                    chunk_number += 1
                await blob_client.commit_block_list(block_ids)

            blob_properties = await blob_client.get_blob_properties()
            if blob_properties.size != file_size:
                raise AzureStorageError("Uploaded file size does not match local file size.")

            azure_url = f"https://{Settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{Settings.AZURE_CONTAINER_NAME}/{azure_path}"

            logger.info(f"Azure upload completed successfully: {azure_url}")
            return azure_url

    except AzureStorageError as e:
        logger.error(f"Azure upload error: {e}")
        raise AzureStorageError(f"Azure upload failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected upload error: {e}")
        raise AzureStorageError(f"Upload failed: {e}")


def upload_file_to_azure_sync(local_path: Path, azure_path: str) -> str:
    """Synchronous version for compatibility"""

    if not local_path.exists():
        raise AzureStorageError(f"Local file not found: {local_path}")

    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            Settings.AZURE_STORAGE_CONNECTION_STRING
        )

        blob_client = blob_service_client.get_blob_client(
            container=Settings.AZURE_CONTAINER_NAME,
            blob=azure_path
        )

        with open(local_path, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True, timeout=Settings.AZURE_UPLOAD_TIMEOUT)

        azure_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{Settings.AZURE_CONTAINER_NAME}/{azure_path}"
        return azure_url

    except Exception as e:
        raise AzureStorageError(f"Azure upload failed: {e}")

async def check_azure_connectivity() -> bool:
    """Check if Azure storage is accessible"""

    try:
        async with BlobServiceClient.from_connection_string(
            Settings.AZURE_STORAGE_CONNECTION_STRING
        ) as client:

            # Try to list containers (minimal operation)
            containers = []
            async for container in client.list_containers():
                containers.append(container.name)
                break  # Just check if we can connect

            return True

    except Exception as e:
        logging.error(f"Azure connectivity check failed: {e}")
        return False

async def estimate_upload_time(file_size_bytes: int, upload_speed: float) -> float:
    """Estimate the upload time based on file size and upload speed."""
    file_size_mb = file_size_bytes / (1024 * 1024)
    file_size_megabits = file_size_mb * 8

    theoretical_time = file_size_megabits / upload_speed

    overhead_factor = 1.25
    estimated_time = theoretical_time * overhead_factor

    return max(5.0, estimated_time)
