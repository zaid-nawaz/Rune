from pathlib import Path

from app.video.ffmpeg import run_ffmpeg

MUSIC_DIR = Path("uploads/music")

def resolve_music_file(music_file: str) -> str:
    path = Path(music_file)

    # Already an existing path
    if path.exists():
        return str(path)

    # LLM selected a filename from the music library
    library_path = MUSIC_DIR / path.name

    if library_path.exists():
        return str(library_path)

    raise FileNotFoundError(
        f"Music file '{music_file}' was not found in {MUSIC_DIR}"
    )

def add_background_music(
    input_path: Path,
    music_file: Path,
    output_path: Path,
    music_volume: float = 0.15,
) -> Path:
    
    music_file = resolve_music_file(music_file)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-stream_loop",
        "-1",
        "-i",
        str(music_file),
        "-filter_complex",
        (
            f"[1:a]volume={music_volume}[music];"
            "[0:a][music]amix=inputs=2:"
            "duration=first:"
            "dropout_transition=2[a]"
        ),
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-c:v",
        "copy",
        "-shortest",
        str(output_path),
    ]

    run_ffmpeg(command)

    return output_path