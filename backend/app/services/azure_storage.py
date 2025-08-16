import uuid
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from app.config import settings


class AzureUploadService:
    def __init__(self):
        self.container_name = settings.AZURE_CONTAINER_NAME
        self.blob_service = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME


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


    def blob_exists(self, file_path: str) -> bool:
        try:
            blob_client = self.blob_service.get_blob_client(
                container=self.container_name,
                blob=file_path
            )
            return blob_client.exists()
        except Exception:
            return False
