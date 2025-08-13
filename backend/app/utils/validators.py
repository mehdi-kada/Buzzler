from pathlib import Path
import logging
import magic
from app.config import Settings

# Custom exception for video validation errors
class VideoValidationError(Exception):
    pass


def validate_video_file(file_content: bytes, filename: str, declared_size: int) -> dict:
    """
    Validates a video file's content, extension, and MIME type.
    Raises VideoValidationError on failure.
    """
    actual_size = len(file_content)
    max_size = Settings.MAX_VIDEO_SIZE_MB

    # Check file size constraints
    if actual_size > max_size * 1024 * 1024:
        raise VideoValidationError(f"File size exceeds the maximum limit of {max_size} MB.")
    if actual_size < 1024:
        raise VideoValidationError(f"File size is too small: {actual_size} bytes.")

    # Warn if declared and actual size differ significantly
    if abs(actual_size - declared_size) > 1024:
        logging.warning(f"File size mismatch: {filename}. Declared: {declared_size}, Actual: {actual_size}")

    path = Path(filename)
    file_extension = path.suffix.lower().lstrip(".")

    # Check allowed extensions (use ALLOWED_VIDEO_FORMATS from config)
    if file_extension not in Settings.ALLOWED_VIDEO_FORMATS:
        raise VideoValidationError(f"Invalid file type: {file_extension}. Allowed types are: {Settings.ALLOWED_VIDEO_FORMATS}")

    # Check MIME type using python-magic
    mime_type = magic.from_buffer(file_content, mime=True)
    if mime_type not in Settings.ALLOWED_MIME_TYPES:
        raise VideoValidationError(f"Invalid MIME type: {mime_type}. Allowed types are: {Settings.ALLOWED_MIME_TYPES}")

    # Check for valid video signature
    if not has_video_signature(file_content):
        raise VideoValidationError("File does not contain a valid video signature.")

    return {
        "filename": filename,
        "file_extension": file_extension,
        "valid": True,
        "file_size": actual_size,
        "mime_type": mime_type
    }


def has_video_signature(file_content: bytes) -> bool:
    """
    Checks for common video file signatures in the first bytes of the file.
    """
    signatures = {
        b'\x00\x00\x00\x14ftypmp4': 'mp4',  # MP4
        b'\x00\x00\x00\x20ftypM4V': 'mp4',  # M4V
        b'\x00\x00\x00\x18ftypmp42': 'mp4', # MP4 v2
        b'RIFF': 'avi',  # AVI (first 4 bytes)
        b'\x1a\x45\xdf\xa3': 'mkv',  # Matroska/MKV
        b'FLV\x01': 'flv',  # FLV
    }
    for signature in signatures:
        if file_content[:32].startswith(signature):
            return True
    # Special case for AVI (RIFF + AVI)
    if file_content[:32].startswith(b'RIFF') and b'AVI ' in file_content[32:]:
        return True
    return False


def get_safe_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitizes a filename by removing unsafe characters and truncating if needed.
    """
    safe_name = Path(filename).name
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    if len(safe_name) > max_length:
        name_part = Path(safe_name).stem
        ext_part = Path(safe_name).suffix
        max_name_length = max_length - len(ext_part)
        safe_name = name_part[:max_name_length] + ext_part
    return safe_name