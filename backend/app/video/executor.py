from pathlib import Path

from app.video.ffmpeg import run_ffmpeg


def execute_ffmpeg_command(
    command: list[str],
) -> None:

    run_ffmpeg(command)