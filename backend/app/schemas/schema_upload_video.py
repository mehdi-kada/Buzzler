from pydantic.main import BaseModel


class VideoRequest(BaseModel):
    file_name: str
    file_path: str
    is_url: bool = False

class VideoUploadCompleteRequest(BaseModel):
    file_size: int
    file_name: str
    azure_blob_url: str
