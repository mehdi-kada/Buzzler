import os
import shutil
from pathlib import Path
from typing import Optional, Tuple
import uuid
import time
import aiofiles
import asyncio
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def get_available_disk_space(path: Path) -> float:
    """Get available disk space in GB"""
    statvfs = os.statvfs(path)
    available_bytes = statvfs.f_frsize * statvfs.f_bavail
    return available_bytes / (1024 ** 3)


def check_storage_capacity(required_size_bytes: int) -> bool:
    """Check if we have enough storage capacity"""
    required_gb = required_size_bytes / (1024 ** 3)
    available_gb = get_available_disk_space(settings.TEMP_BASE_DIR)
    
    needed_gb = (required_gb * 2) + 2
    
    if available_gb < needed_gb:
        logger.warning(
            f"Insufficient storage: need {needed_gb:.2f}GB, available {available_gb:.2f}GB"
        )
        return False
    
    return True

def generate_unique_paths(user_id: int, filename: str) -> Tuple[Path, Path, str]:
    """Generate unique paths for video and audio files"""
    
    file_uuid = str(uuid.uuid4())
    timestamp = int(time.time())
    
    # Create user-specific directories
    user_video_dir = settings.TEMP_BASE_DIR / "videos" / str(user_id)
    user_audio_dir = settings.TEMP_BASE_DIR / "audio" / str(user_id)
    
    user_video_dir.mkdir(parents=True, exist_ok=True)
    user_audio_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filenames
    file_ext = Path(filename).suffix.lower()
    video_filename = f"{file_uuid}_{timestamp}{file_ext}"
    audio_filename = f"{file_uuid}_{timestamp}.mp3"
    
    temp_video_path = user_video_dir / video_filename
    temp_audio_path = user_audio_dir / audio_filename
    
    # Azure path
    azure_path = f"videos/{user_id}/{video_filename}"
    
    return temp_video_path, temp_audio_path, azure_path

async def save_uploaded_file(file_content: bytes, file_path: Path) -> bool:
    """Save uploaded file content to disk asynchronously"""
    
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Verify file was written correctly
        if file_path.exists() and file_path.stat().st_size == len(file_content):
            logger.info(f"Successfully saved file: {file_path}")
            return True
        else:
            logger.error(f"File save verification failed: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {e}")
        if file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        return False

def cleanup_file(file_path: Path) -> bool:
    """Safely remove a file"""
    
    if not file_path or not file_path.exists():
        return True
    
    try:
        file_path.unlink()
        logger.info(f"Cleaned up file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {e}")
        return False

def cleanup_user_temp_files(user_id: int, older_than_hours: int = 0) -> int:
    """Clean up all temp files for a user"""
    
    if older_than_hours is 0:
        older_than_hours = settings.TEMP_FILE_TTL_HOURS
        
    cutoff_time = time.time() - (older_than_hours * 3600)
    cleaned_count = 0
    
    user_dirs = [
        settings.TEMP_BASE_DIR / "videos" / str(user_id),
        settings.TEMP_BASE_DIR / "audio" / str(user_id)
    ]
    
    for user_dir in user_dirs:
        if not user_dir.exists():
            continue
            
        for file_path in user_dir.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                if cleanup_file(file_path):
                    cleaned_count += 1
    
    return cleaned_count

async def get_file_info(file_path: Path) -> Optional[dict]:
    """Get file information asynchronously"""
    
    if not file_path.exists():
        return None
    
    try:
        stat = file_path.stat()
        return {
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'exists': True
        }
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return None
