from pathlib import Path

from app.video.ffmpeg import run_ffmpeg

def change_volume(
    input_path: Path,
    output_path: Path,
    volume: float,
) -> Path:

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-filter:a",
        f"volume={volume}",
        "-c:v",
        "copy",
        str(output_path),
    ]

    run_ffmpeg(command)

    return output_path