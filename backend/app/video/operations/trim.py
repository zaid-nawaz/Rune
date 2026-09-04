from pathlib import Path

from app.video.ffmpeg import run_ffmpeg


def trim_video(
    input_path: Path,
    output_path: Path,
    start: float,
    duration: float,
) -> Path:

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start),
        "-i",
        str(input_path),
        "-t",
        str(duration),
        "-c",
        "copy",
        str(output_path),
    ]

    run_ffmpeg(command)

    return output_path