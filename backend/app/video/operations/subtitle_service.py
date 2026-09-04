from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock

import whisper


@dataclass
class Word:
    text: str
    start: float
    end: float


@dataclass
class Caption:
    text: str
    start: float
    end: float
    words: list[Word]


class WhisperSubtitleService:
    """
    Handles speech-to-text transcription and extraction
    of word-level timestamps.
    """

    def __init__(
        self,
        model_name: str = "base",
    ):
        self.model_name = model_name

        self.model = whisper.load_model(model_name)

        # Whisper's word-timestamp alignment path uses
        # temporary internal hooks. Keeping access serialized
        # avoids concurrent transcription problems.
        self._lock = Lock()

    def transcribe(
        self,
        video_path: str | Path,
        language: str | None = None,
    ) -> list[Word]:

        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(
                f"Video file does not exist: {video_path}"
            )

        with self._lock:

            result = self.model.transcribe(
                str(video_path),
                language=language,
                task="transcribe",
                word_timestamps=True,
                verbose=False,
                fp16=False,
            )

        words: list[Word] = []

        for segment in result["segments"]:

            for word in segment.get("words", []):

                text = word["word"].strip()

                if not text:
                    continue

                start = float(word["start"])
                end = float(word["end"])

                if end <= start:
                    continue

                words.append(
                    Word(
                        text=text,
                        start=start,
                        end=end,
                    )
                )

        return words
    
def build_captions(
    words: list[Word],
    *,
    max_words: int = 7,
    max_chars: int = 42,
    max_duration: float = 3.5,
    pause_threshold: float = 0.7,
) -> list[Caption]:

    if not words:
        return []

    captions: list[Caption] = []

    current_words: list[Word] = []

    def flush():
        if not current_words:
            return

        captions.append(
            Caption(
                text=" ".join(
                    word.text
                    for word in current_words
                ).strip(),
                start=current_words[0].start,
                end=current_words[-1].end,
                words=current_words.copy(),
            )
        )

        current_words.clear()

    for word in words:

        if not current_words:
            current_words.append(word)
            continue

        previous = current_words[-1]

        gap = word.start - previous.end

        current_text = " ".join(
            w.text for w in current_words
        )

        new_text = f"{current_text} {word.text}"

        duration = word.end - current_words[0].start

        should_break = (
            len(current_words) >= max_words
            or len(new_text) > max_chars
            or duration > max_duration
            or gap >= pause_threshold
        )

        if should_break:
            flush()

        current_words.append(word)

    flush()

    return captions