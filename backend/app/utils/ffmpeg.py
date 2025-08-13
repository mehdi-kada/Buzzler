import asyncio
from math import log
from os import error
from sys import stderr, stdout
from venv import logger
from anyio import Path

from backend.app.config import Settings
from backend.app.models import video


class FFMPEGException(Exception):
    pass

async def extract_audio(video_path : Path, audio_path: Path, progress_callback=None ) -> bool:
    
    if not await video_path.exists():
        raise FFMPEGException(f"Video file {video_path} does not exist.")

    await audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        Settings.FFMPEG_PATH,
        '-i', str(video_path),
        '-vn', 
        '-acodec', 'mp3',
        '-ab', Settings.AUDIO_BITRATE,
        '-ar', Settings.AUDIO_SAMPLE_RATE,
        '-ac', '2',  
        '-map_metadata', '-1',  
        '-y',  
        str(audio_path)
    ]
    
    logger.info(f"starting audio extraction from {video_path} to {audio_path}")
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            if await audio_path.exists():
                stat = await audio_path.stat()
                if stat.st_size > 0:
                    logger.info(f"Audio extraction successful: {audio_path}")
                    return True
                else:
                    raise FFMPEGException(f"Audio extraction failed: {audio_path} is empty.")
            else:
                raise FFMPEGException(f"Audio extraction failed: {audio_path} does not exist.")
        else:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise FFMPEGException(f"FFmpeg process failed with return code {process.returncode}: {error_msg}")
        

        
    except asyncio.TimeoutError:
        raise FFMPEGException("FFmpeg process timed out.")
    except Exception as e:
        logger.error(f"FFmpeg process failed: {e}")
        raise FFMPEGException(f"FFmpeg process failed: {e}")
