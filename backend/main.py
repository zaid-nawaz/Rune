from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware

from app.agent.graph import build_graph


app = FastAPI(title="Rune Video Editor")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
MUSIC_DIR = UPLOAD_DIR / "music"
OUTPUT_DIR = Path("outputs/jobs")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg"}


async def save_file(file: UploadFile, path: Path):
    with path.open("wb") as f:
        while chunk := await file.read(1024 * 1024):
            f.write(chunk)
    await file.close()


def cleanup(path: Path):
    shutil.rmtree(path, ignore_errors=True)


def get_music_library():
    return [
        file.name
        for file in MUSIC_DIR.iterdir()
        if file.is_file() and file.suffix.lower() in AUDIO_EXTENSIONS
    ]


@app.get("/")
def root():
    return {"message": "Rune Video Editor API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/edit")
async def edit_video(
    video: UploadFile = File(...),
    instruction: str = Form(...),
    music: UploadFile | None = File(None),
):
    video_ext = Path(video.filename or "").suffix.lower()

    if video_ext not in VIDEO_EXTENSIONS:
        raise HTTPException(400, "Unsupported video format")

    if not instruction.strip():
        raise HTTPException(400, "Instruction cannot be empty")

    job_id = str(uuid4())
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True)

    input_path = job_dir / f"input{video_ext}"
    output_path = job_dir / "output.mp4"

    try:
        await save_file(video, input_path)

        agent_instruction = instruction.strip()

        # User uploaded music
        if music:
            music_ext = Path(music.filename or "").suffix.lower()

            if music_ext not in AUDIO_EXTENSIONS:
                raise HTTPException(400, "Unsupported music format")

            music_path = job_dir / f"music{music_ext}"
            await save_file(music, music_path)

            agent_instruction += (
                f"\n\nThe user uploaded a music file: {music_path}\n"
                "If the user asks for background music, use this uploaded file."
            )

        # No music uploaded → expose music library to agent
        else:
            music_library = get_music_library()

            agent_instruction += (
                "\n\nAvailable background music:\n"
                + (
                    "\n".join(f"- {name}" for name in music_library)
                    if music_library
                    else "- No music files are currently available."
                )
                + "\n\n"
                "If the user asks for background music and did not upload "
                "a music file, choose the most appropriate music from the "
                "available files based on their filenames."
            )

        graph = build_graph()

        result = graph.invoke({
            "user_request": agent_instruction,
            "input_path": str(input_path),
            "output_path": str(output_path),
        })

        if result.get("error"):
            raise RuntimeError(result["error"])

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("Editing completed without producing a valid video")

        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename="edited_video.mp4",
            background=BackgroundTask(cleanup, job_dir),
        )

    except HTTPException:
        cleanup(job_dir)
        raise

    except Exception as e:
        cleanup(job_dir)
        raise HTTPException(500, str(e)) from e