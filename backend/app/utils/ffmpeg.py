import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict

from app.config import Settings

class FFMPEGException(Exception):
    pass


logger = logging.getLogger(__name__)


async def extract_audio(video_path: Path, audio_path: Path, progress_callback=None) -> bool:
    """Extract audio from `video_path` into `audio_path` using ffmpeg.

    This file uses synchronous pathlib.Path operations for filesystem checks.
    """

    if not video_path.exists():
        raise FFMPEGException(f"Video file {video_path} does not exist.")

    audio_path.parent.mkdir(parents=True, exist_ok=True)

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
        str(audio_path),
    ]

    logger.info("starting audio extraction from %s to %s", video_path, audio_path)
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=300)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise FFMPEGException("FFmpeg process timed out.")

        if process.returncode == 0:
            if audio_path.exists():
                stat = audio_path.stat()
                if stat.st_size > 0:
                    logger.info("Audio extraction successful: %s", audio_path)
                    return True
                else:
                    raise FFMPEGException(f"Audio extraction failed: {audio_path} is empty.")
            else:
                raise FFMPEGException(f"Audio extraction failed: {audio_path} does not exist.")
        else:
            error_msg = stderr_bytes.decode() if stderr_bytes else "Unknown error"
            raise FFMPEGException(
                f"FFmpeg process failed with return code {process.returncode}: {error_msg}"
            )
    except Exception as e:
        logger.exception("FFmpeg process failed")
        raise FFMPEGException(f"FFmpeg process failed: {e}")


async def get_video_info_async(video_path: Path) -> Dict[str, Any]:
    """Get video information using ffprobe asynchronously.

    Ensures ffprobe emits JSON (`-print_format json`) and returns parsed dict.
    """
    if not video_path.exists():
        raise FFMPEGException(f"Video file {video_path} does not exist.")

    cmd = [
        Settings.FFPROBE_PATH,
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        str(video_path),
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=60)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise FFMPEGException("FFprobe process timed out.")

    if process.returncode != 0:
        error_msg = stderr_bytes.decode() if stderr_bytes else "Unknown error"
        raise FFMPEGException(
            f"FFprobe process failed with return code {process.returncode}: {error_msg}"
        )

    out = stdout_bytes.decode() if stdout_bytes else ""
    try:
        data = json.loads(out)
    except json.JSONDecodeError as e:
        raise FFMPEGException(f"Failed to parse ffprobe output: {e}; output={out!r}")

    return data


def _parse_video_info(ffprobe_data: dict) -> Dict[str, Any]:
    """Parse ffprobe output into structured video information"""

    video_stream = None
    audio_stream = None

    for stream in ffprobe_data.get('streams', []):
        if stream.get('codec_type') == 'video' and video_stream is None:
            video_stream = stream
        elif stream.get('codec_type') == 'audio' and audio_stream is None:
            audio_stream = stream

    if not video_stream:
        raise FFMPEGException("No video stream found in file")

    duration = None
    if 'duration' in ffprobe_data.get('format', {}):
        duration = float(ffprobe_data['format']['duration'])
    elif 'duration' in video_stream:
        duration = float(video_stream['duration'])

    fps = 0.0
    if 'r_frame_rate' in video_stream:
        fps_str = video_stream['r_frame_rate']
        if '/' in fps_str:
            num, den = fps_str.split('/')
            if int(den) != 0:
                fps = round(float(num) / float(den), 2)

    width = video_stream.get('width', 0)
    height = video_stream.get('height', 0)

    return {
        'duration': duration,
        'width': width,
        'height': height,
        'fps': fps,
        'video_codec': video_stream.get('codec_name', 'unknown'),
        'audio_codec': audio_stream.get('codec_name', 'unknown') if audio_stream else None,
        'bitrate': int(ffprobe_data.get('format', {}).get('bit_rate', 0)),
        'file_size': int(ffprobe_data.get('format', {}).get('size', 0)),
        'has_audio': audio_stream is not None,
    }


def estimate_audio_extraction_time(video_duration: float, file_size_mb: float) -> float:
    """Estimate audio extraction time in seconds"""
    base_time = video_duration * 0.1
    size_overhead = file_size_mb * 0.02
    estimated_time = max(2.0, min(120.0, base_time + size_overhead))
    return estimated_time
