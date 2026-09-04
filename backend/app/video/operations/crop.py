from pathlib import Path

from app.video.ffmpeg import run_ffmpeg

def crop_video(
    input_path: Path,
    output_path: Path,
    width: int,
    height: int,
) -> Path:

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vf",
        f"crop={width}:{height}",
        "-c:a",
        "copy",
        str(output_path),
    ]

    run_ffmpeg(command)

    return output_path