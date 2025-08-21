from pydantic.main import BaseModel
from typing import Optional


class VideoRequest(BaseModel):
    file_name: str
    file_path: Optional[str] = None
    is_url: bool = False

class VideoUploadCompleteRequest(BaseModel):
    file_size: int
    file_name: str
    azure_blob_url: str
