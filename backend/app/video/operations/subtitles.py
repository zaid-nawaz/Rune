from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from app.video.operations.subtitle_service import (
    Caption,
    WhisperSubtitleService,
    build_captions,
)


def format_srt_time(seconds: float) -> str:

    milliseconds = round(seconds * 1000)

    hours = milliseconds // 3600000
    milliseconds %= 3600000

    minutes = milliseconds // 60000
    milliseconds %= 60000

    secs = milliseconds // 1000
    ms = milliseconds % 1000

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d},"
        f"{ms:03d}"
    )


def build_srt(captions: list[Caption]) -> str:

    blocks = []

    for index, caption in enumerate(captions, start=1):

        blocks.append(
            f"{index}\n"
            f"{format_srt_time(caption.start)} --> "
            f"{format_srt_time(caption.end)}\n"
            f"{caption.text}\n"
        )

    return "\n".join(blocks) + "\n"


def render_subtitles(
    video_path: str,
    captions: list[Caption],
    output_path: str,
) -> str:

    video_path = Path(video_path)
    output_path = Path(output_path)

    if not video_path.exists():
        raise FileNotFoundError(video_path)

    if not captions:
        raise ValueError("No captions provided.")

    srt_content = build_srt(captions)

    with tempfile.TemporaryDirectory() as temp_dir:

        srt_path = Path(temp_dir) / "captions.srt"

        srt_path.write_text(
            srt_content,
            encoding="utf-8",
        )

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vf",
            f"subtitles={srt_path}",
            "-c:a",
            "copy",
            str(output_path),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:

            raise RuntimeError(
                "Subtitle rendering failed:\n"
                + result.stderr
            )

    return str(output_path)


_subtitle_service: WhisperSubtitleService | None = None


def get_subtitle_service() -> WhisperSubtitleService:
    """
    Lazily create the Whisper service.

    The Whisper model is loaded only once and reused for
    future subtitle operations.
    """

    global _subtitle_service

    if _subtitle_service is None:
        print("Loading Whisper subtitle model...")

        _subtitle_service = WhisperSubtitleService(
            model_name="base"
        )

    return _subtitle_service


def add_subtitles(
    input_path: str,
    output_path: str,
    *,
    language: str | None = None,
) -> str:
    """
    Complete subtitle operation.

    1. Transcribe video using Whisper
    2. Extract word timestamps
    3. Group words into captions
    4. Render plain SRT subtitles
    5. Burn subtitles into output video
    """

    print("Generating subtitles...")

    subtitle_service = get_subtitle_service()

    print("Transcribing audio...")

    words = subtitle_service.transcribe(
        input_path,
        language=language,
    )

    if not words:
        raise ValueError(
            "No speech was detected in the video."
        )

    print(
        f"Detected {len(words)} words."
    )

    captions = build_captions(
        words,
        max_words=7,
        max_chars=42,
        max_duration=3.5,
        pause_threshold=0.7,
    )

    print(
        f"Generated {len(captions)} captions."
    )

    print("Rendering subtitles...")

    return render_subtitles(
        video_path=input_path,
        captions=captions,
        output_path=output_path,
    )