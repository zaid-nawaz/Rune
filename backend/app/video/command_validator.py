from pathlib import Path


FORBIDDEN_ARGUMENTS = {
    "sh",
    "bash",
    "cmd",
    "powershell",
}


def validate_ffmpeg_command(
    command: list[str],
) -> None:

    if not command:
        raise ValueError(
            "FFmpeg command is empty."
        )

    if command[0] != "ffmpeg":
        raise ValueError(
            "Command must start with ffmpeg."
        )

    for argument in command:

        if any(
            character in argument
            for character in [
                ";",
                "&&",
                "||",
                "`",
                "$(",
                ">",
                "<",
                "|",
            ]
        ):
            raise ValueError(
                "Potentially unsafe shell syntax "
                f"detected: {argument}"
            )

        if argument.lower() in FORBIDDEN_ARGUMENTS:
            raise ValueError(
                f"Forbidden executable: {argument}"
            )

    if "INPUT_VIDEO" not in command:
        raise ValueError(
            "Command must contain INPUT_VIDEO."
        )

    if "OUTPUT_VIDEO" not in command:
        raise ValueError(
            "Command must contain OUTPUT_VIDEO."
        )