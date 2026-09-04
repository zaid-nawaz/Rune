import subprocess
from pathlib import Path
import json

def run_ffmpeg(command: list[str]) -> None:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg failed:\n{result.stderr}"
        )
        


def get_video_info(input_path: Path) -> dict:
    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(input_path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFprobe failed:\n{result.stderr}"
        )

    data = json.loads(result.stdout)

    video_stream = next(
        (
            stream
            for stream in data["streams"]
            if stream["codec_type"] == "video"
        ),
        None,
    )

    audio_stream = next(
        (
            stream
            for stream in data["streams"]
            if stream["codec_type"] == "audio"
        ),
        None,
    )

    return {
        "duration": float(data["format"]["duration"]),
        "width": video_stream["width"] if video_stream else None,
        "height": video_stream["height"] if video_stream else None,
        "video_codec": (
            video_stream["codec_name"]
            if video_stream
            else None
        ),
        "audio_codec": (
            audio_stream["codec_name"]
            if audio_stream
            else None
        ),
        "has_audio": audio_stream is not None,
    }
    






