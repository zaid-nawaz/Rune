# Rune

Rune turns a plain-English video-editing instruction into an actual edited video.

Upload a video, describe what you want ("trim to the first 30 seconds, add subtitles, and lower the volume by half"), and Rune plans the edit with an LLM, then executes it with FFmpeg, retrying automatically if a step fails.

```
POST /edit
  video: your video file
  instruction: "trim to 30s and add subtitles"
  music: (optional) a background track to mix in
-> returns the edited video
```

## How it works

Rune is a small agent built with [LangGraph](https://github.com/langchain-ai/langgraph), wrapped in a FastAPI backend.

```
analyzer -> planner -> validator -> executor -> observer
               ^______________________________|
               (replans on failure, up to 3 attempts)
```

1. **Analyzer** inspects the uploaded video with `ffprobe` (duration, resolution, codecs, audio).
2. **Planner** sends your instruction plus that video info to an LLM (`gpt-4o-mini`, via OpenRouter), which returns a structured plan: a list of operations, not raw FFmpeg commands.
3. **Validator** checks every operation in the plan is one Rune actually knows how to run.
4. **Executor** runs each operation's FFmpeg command in sequence, chaining outputs into inputs.
5. **Observer** re-inspects the final file to confirm it's a valid, non-empty video.

If validation or execution fails, the error is fed back into the planner, which produces a corrected plan, up to 3 attempts before giving up.

### Available operations

| Operation | What it does |
|---|---|
| `trim` | Cut a segment out of the video |
| `crop` | Crop to a given width/height |
| `resize` | Scale to a given width/height |
| `volume` | Adjust audio volume |
| `background_music` | Mix in a music track (uploaded, or picked from the built-in library) |
| `subtitles` | Transcribe speech with Whisper and burn in plain SRT captions |

Anything outside those six, the planner falls back to `custom_ffmpeg`: a second LLM call turns your description into an FFmpeg command, which is checked against a strict validator (no shell operators, no shell executables, must start with `ffmpeg`) before it's run as a plain argument list, never through a shell.

## Project structure

```
backend/
├── main.py                          FastAPI app, the /edit endpoint
├── app/
│   ├── agent/                       the LangGraph agent
│   │   ├── graph.py                 builds the state graph and its retry routing
│   │   ├── state.py                 the shared state passed between nodes
│   │   ├── analyzer.py              ffprobe inspection node
│   │   ├── planner.py               LLM planning node
│   │   ├── prompts.py               the planner's system prompt
│   │   ├── validator.py             plan validation node
│   │   └── observer.py              output verification node
│   └── video/                       the actual FFmpeg editing logic
│       ├── registry.py              operation name to function mapping
│       ├── plan_executor.py         runs a plan's operations in sequence
│       ├── ffmpeg.py                run_ffmpeg() / get_video_info()
│       ├── custom_ffmpeg.py         LLM-generated command (for the fallback)
│       ├── command_validator.py     safety checks on generated commands
│       ├── custom_executor.py       runs the generated command
│       └── operations/              trim, crop, resize, volume, music, subtitles
└── uploads/music/                   built-in background music library
```

## Setup

Requires Python 3.12+, [`uv`](https://docs.astral.sh/uv/), and `ffmpeg`/`ffprobe` on your `PATH`.

```bash
cd backend
uv sync
```

Create a `.env` file in `backend/` with:

```
OPENROUTER_API_KEY=your-key-here
```

Run the API:

```bash
uv run uvicorn main:app --reload
```

Try it:

```bash
curl -X POST http://localhost:8000/edit \
  -F "video=@/path/to/your/video.mp4" \
  -F "instruction=trim to the first 10 seconds and add subtitles" \
  --output edited.mp4
```

## Design notes

A few deliberate choices worth knowing about:

- **Subtitles use plain SRT, not ASS.** An earlier version supported styled presets (TikTok-style highlighting, karaoke-style word coloring) via hand-built ASS files. That was simplified down to plain, readable captions, since FFmpeg's `subtitles` filter handles both formats identically and SRT needs none of ASS's positional styling syntax.
- **Custom FFmpeg commands are never run through a shell.** The LLM that generates them is instructed to avoid shell metacharacters and quote characters, a validator rejects anything containing them, and the command is executed as a plain argument list (`subprocess.run([...])`), not a shell string, so even a malformed generated command can't chain into a second command.
- **A fresh graph is built per request** rather than reused across requests, and each job gets its own directory under `outputs/jobs/`, deleted automatically once the response is sent.
