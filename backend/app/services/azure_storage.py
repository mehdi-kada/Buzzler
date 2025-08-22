import uuid
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import AzureError
from app.config import settings
import base64
from typing import Optional
from typing import Callable
import io


class AzureUploadService:
    def __init__(self):
        self.container_name = settings.AZURE_CONTAINER_NAME
        self.blob_service = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.chunk_size = 4 *1024 * 1024  # 4 MB
        

    def generate_sas(self, file_name: str) -> tuple[str, str]:
        unique_id = str(uuid.uuid4())
        file_path = f"{unique_id}/{file_name}"

        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            blob_name=file_path,
            account_key=self._get_account_key(),
            permission=BlobSasPermissions(write=True, create=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        blob_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{file_path}"
        sas_url = f"{blob_url}?{sas_token}"

        return sas_url, file_path

    def _get_account_key(self) -> str:
        """Extract account key from connection string."""
        connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        for part in connection_string.split(';'):
            if part.startswith('AccountKey='):
                return part.split('=', 1)[1]
        raise ValueError("AccountKey not found in connection string")


    def get_blob_url(self, file_path: str) -> str:
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{file_path}"

    def delete_blob(self, file_path: str) -> bool:
        try:
            blob_client = self.blob_service.get_blob_client(
                container=self.container_name,
                blob=file_path
            )
            blob_client.delete_blob()
            return True
        except Exception as e:
            print(f"Error deleting blob {file_path}: {e}")
            return False
    
        def upload_stream_in_blocks(
            self, 
            blob_name: str, 
            data_stream: io.BytesIO,
            progress_callback: Optional[Callable] = None
        ) -> str:
            """Upload stream data using Azure's block upload mechanism."""
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            
            block_list = []
            block_id_counter = 0
            total_size = 0
            
            try:
                while True:
                    chunk = data_stream.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    # Create block ID
                    block_id = base64.b64encode(f"{block_id_counter:010d}".encode()).decode()
                    
                    # Stage block
                    blob_client.stage_block(block_id, chunk)
                    block_list.append(block_id)
                    
                    block_id_counter += 1
                    total_size += len(chunk)
                    
                    if progress_callback:
                        progress_callback({
                            'uploaded_bytes': total_size,
                            'chunk_size': len(chunk),
                            'blocks_uploaded': len(block_list)
                        })
                
                # Commit all blocks
                if block_list:
                    blob_client.commit_block_list(block_list)
                
                return blob_name
                
            except AzureError as e:
                # Clean up any staged blocks
                try:
                    blob_client.delete_blob()
                except:
                    pass
                raise Exception(f"Azure upload failed: {str(e)}")

    def blob_exists(self, file_path: str) -> bool:
        try:
            blob_client = self.blob_service.get_blob_client(
                container=self.container_name,
                blob=file_path
            )
            return blob_client.exists()
        except Exception:
            return False
