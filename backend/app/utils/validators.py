

class VedioValidationError(Exception):
    pass

def validate_video_file(file_content: bytes, filename: str, declared_size: int) -> dict:

    actual_size = len(file_content)
    max_size = Settings.MAX_VIDEO_SIZE_MB

    if actual_size > max_size * 1024 * 1024:
        raise VedioValidationError(f"File size exceeds the maximum limit of {max_size} MB.")

    if actual_size < 1024:
        raise VedioValidationError(f"File size is too small: {actual_size} bytes.")

    if abs(actual_size - declared_size) > 1024:
        logger.warning(f"File size mismatch: {filename}. Declared: {declared_size}, Actual: {actual_size}")

    path = Path(filename)
    file_extension = path.suffix.lower().lstrip(".")

    if file_extension not in Settings.ALLOWED_VIDEO_EXTENSIONS:
        raise VedioValidationError(f"Invalid file type: {file_extension}. Allowed types are: {Settings.ALLOWED_VIDEO_EXTENSIONS}")

    mime_type = magic.from_buffer(file_content, mime=True)
    if mime_type not in Settings.ALLOWED_VIDEO_MIME_TYPES:
        raise VedioValidationError(f"Invalid MIME type: {mime_type}. Allowed types are: {Settings.ALLOWED_VIDEO_MIME_TYPES}")

    if not has_video_signature(file_content):
        raise VedioValidationError(f"File does not contain a valid video signature.")

    return {
        "filename": filename,
        "file_extension": file_extension,
        "valid": true,
        "file_size": actual_size,
        "mime_type": mime_type
    }


def has_video_signature(file_content: bytes) -> bool:

    signatures = {
        b'\x00\x00\x00\x14ftypmp4': 'mp4',  # MP4
        b'\x00\x00\x00\x20ftypM4V': 'mp4',  # M4V
        b'\x00\x00\x00\x18ftypmp42': 'mp4', # MP4 v2
        b'RIFF': 'avi',  # AVI (first 4 bytes)
        b'\x1a\x45\xdf\xa3': 'mkv',  # Matroska/MKV
        b'FLV\x01': 'flv',  # FLV
    }

    for signature, format_type in signatures.items():
        if file_content[:32].startswith(signature):
            return True

    # special case for AVI (RIFF + AVI)
    if file_content[:32].startswith(b'RIFF') and b'AVI ' in file_content[32:]:
        return True

    return False


def get_safe_filename(filename: str, max_length: int = 100) -> str:
    
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