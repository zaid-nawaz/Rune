from pathlib import Path

from app.video.custom_ffmpeg import (
    generate_ffmpeg_command,
)

from app.video.command_validator import (
    validate_ffmpeg_command,
)

from app.video.ffmpeg import (
    run_ffmpeg,
)


def execute_custom_ffmpeg(
    description: str,
    input_path: Path,
    output_path: Path,
) -> Path:

    generated = generate_ffmpeg_command(
        description
    )

    command = generated.command

    validate_ffmpeg_command(command)

    command = [
        argument.replace(
            "INPUT_VIDEO",
            str(input_path),
        ).replace(
            "OUTPUT_VIDEO",
            str(output_path),
        )
        for argument in command
    ]

    print("\nGenerated FFmpeg command:")
    print(command)

    run_ffmpeg(command)

    return output_path