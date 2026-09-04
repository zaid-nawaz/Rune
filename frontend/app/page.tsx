"use client";

import {
  ChangeEvent,
  DragEvent,
  useEffect,
  useRef,
  useState,
} from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const EXAMPLES = [
  "Trim the first 10 seconds and add captions.",
  "Make this video vertical for Instagram Reels.",
  "Remove the original audio and add background music.",
  "Add clean subtitles and make the video brighter.",
];

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Home() {
  const [video, setVideo] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState("");
  const [music, setMusic] = useState<File | null>(null);
  const [instruction, setInstruction] = useState("");
  const [outputUrl, setOutputUrl] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState("");

  const [health, setHealth] = useState<
    "checking" | "online" | "offline"
  >("checking");

  const [dragging, setDragging] = useState(false);

  const videoInput = useRef<HTMLInputElement>(null);
  const musicInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((response) => {
        setHealth(response.ok ? "online" : "offline");
      })
      .catch(() => {
        setHealth("offline");
      });
  }, []);

  useEffect(() => {
    if (!video) {
      setVideoUrl("");
      return;
    }

    const url = URL.createObjectURL(video);

    setVideoUrl(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [video]);

  const acceptVideo = (file: File | undefined) => {
    if (!file) return;

    const allowed = [
      ".mp4",
      ".mov",
      ".mkv",
      ".avi",
      ".webm",
    ];

    const extension =
      "." + (file.name.split(".").pop() || "").toLowerCase();

    if (!allowed.includes(extension)) {
      setError(
        "Unsupported video format. Use MP4, MOV, MKV, AVI, or WEBM.",
      );
      return;
    }

    setError("");
    setVideo(file);
  };

  const acceptMusic = (file: File | undefined) => {
    if (!file) return;

    const allowed = [
      ".mp3",
      ".wav",
      ".m4a",
      ".aac",
      ".ogg",
    ];

    const extension =
      "." + (file.name.split(".").pop() || "").toLowerCase();

    if (!allowed.includes(extension)) {
      setError(
        "Unsupported music format. Use MP3, WAV, M4A, AAC, or OGG.",
      );
      return;
    }

    setError("");
    setMusic(file);
  };

  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();

    setDragging(false);

    acceptVideo(event.dataTransfer.files?.[0]);
  };

  const submit = async () => {
    setError("");

    if (!video) {
      setError("Choose a video first.");
      return;
    }

    if (!instruction.trim()) {
      setError("Tell Rune what you want changed.");
      return;
    }

    setIsEditing(true);

    try {
      setOutputUrl("");

      const formData = new FormData();

      formData.append("video", video);
      formData.append(
        "instruction",
        instruction.trim(),
      );

      if (music) {
        formData.append("music", music);
      }

      const response = await fetch(`${API_URL}/edit`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let message =
          "Rune could not edit this video.";

        try {
          const data = await response.json();

          if (data?.detail) {
            message = data.detail;
          }
        } catch {
          // Ignore JSON parsing failure.
        }

        throw new Error(message);
      }

      const blob = await response.blob();

      const url = URL.createObjectURL(blob);

      setOutputUrl(url);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong.",
      );
    } finally {
      setIsEditing(false);
    }
  };

  return (
    <main className="page-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">R</div>

          <div>
            <div className="brand-name">RUNE</div>

            <div className="brand-subtitle">
              AI VIDEO EDITOR
            </div>
          </div>
        </div>

        <div className="status">
          <span
            className={`status-dot ${health}`}
          />

          {health === "online"
            ? "API connected"
            : health === "offline"
              ? "API offline"
              : "Checking API"}
        </div>
      </header>

      <section className="hero">
        <div className="eyebrow">
          NATURAL LANGUAGE VIDEO EDITING
        </div>

        <h1>Tell Rune what to edit.</h1>

        <p>
          Upload a video, describe the changes in
          plain English, and let the editing agent
          handle the rest.
        </p>
      </section>

      <section className="workspace">
        <div className="panel">
          <div className="panel-heading">
            <div>
              <span className="step">01</span>

              <h2>Source video</h2>
            </div>

            {video && (
              <button
                className="text-button"
                onClick={() => setVideo(null)}
              >
                Remove
              </button>
            )}
          </div>

          {!video ? (
            <div
              className={`dropzone ${
                dragging ? "dragging" : ""
              }`}
              onDragOver={(event) => {
                event.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              onClick={() =>
                videoInput.current?.click()
              }
            >
              <div className="upload-icon">
                ↑
              </div>

              <strong>
                Drop your video here
              </strong>

              <span>
                or click to browse
              </span>

              <small>
                MP4 · MOV · MKV · AVI · WEBM
              </small>

              <input
                ref={videoInput}
                type="file"
                accept="video/*"
                hidden
                onChange={(
                  event: ChangeEvent<HTMLInputElement>,
                ) =>
                  acceptVideo(
                    event.target.files?.[0],
                  )
                }
              />
            </div>
          ) : (
            <div className="file-card">
              <div className="file-icon">
                ▶
              </div>

              <div className="file-info">
                <strong>{video.name}</strong>

                <span>
                  {formatBytes(video.size)}
                </span>
              </div>

              <button
                className="icon-button"
                onClick={() => setVideo(null)}
              >
                ×
              </button>
            </div>
          )}

          {video && videoUrl && (
            <video
              className="source-preview"
              src={videoUrl}
              controls
            />
          )}
        </div>

        <div className="panel instruction-panel">
          <div className="panel-heading">
            <div>
              <span className="step">02</span>

              <h2>
                Editing instruction
              </h2>
            </div>
          </div>


          <textarea
            value={instruction}
            onChange={(event) =>
              setInstruction(event.target.value)
            }
            placeholder="e.g. Remove the first 5 seconds, add modern subtitles, and lower the background music..."
            rows={7}
          />

          <div className="examples">
            <span>Try:</span>

            {EXAMPLES.map((example) => (
              <button
                key={example}
                onClick={() =>
                  setInstruction(example)
                }
              >
                {example}
              </button>
            ))}
          </div>

          <div className="music-section">
            <div className="music-header">
              <div>
                <span className="step">03</span>

                <h2>
                  Music{" "}
                  <em>optional</em>
                </h2>
              </div>

              {music && (
                <button
                  className="text-button"
                  onClick={() =>
                    setMusic(null)
                  }
                >
                  Remove
                </button>
              )}
            </div>

            {!music ? (
              <button
                className="music-picker"
                onClick={() =>
                  musicInput.current?.click()
                }
              >
                <span className="music-plus">
                  +
                </span>

                <span>
                  <strong>
                    Upload music
                  </strong>

                  <small>
                    or let Rune choose from
                    its library
                  </small>
                </span>
              </button>
            ) : (
              <div className="file-card compact">
                <div className="file-icon">
                  ♪
                </div>

                <div className="file-info">
                  <strong>
                    {music.name}
                  </strong>

                  <span>
                    {formatBytes(music.size)}
                  </span>
                </div>

                <button
                  className="icon-button"
                  onClick={() =>
                    setMusic(null)
                  }
                >
                  ×
                </button>
              </div>
            )}

            <input
              ref={musicInput}
              type="file"
              accept="audio/*"
              hidden
              onChange={(event) =>
                acceptMusic(
                  event.target.files?.[0],
                )
              }
            />
          </div>
        </div>
      </section>

      {error && (
        <div className="error-banner">
          ⚠ {error}
        </div>
      )}

      <button
        className="edit-button"
        disabled={
          isEditing ||
          !video ||
          !instruction.trim()
        }
        onClick={submit}
      >
        {isEditing ? (
          <>
            <span className="spinner" />

            Rune is editing…
          </>
        ) : (
          <>
            Edit video <span>→</span>
          </>
        )}
      </button>

      {isEditing && (
        <div className="processing">
          <div className="processing-line">
            <span className="pulse" />

            <span>
              Rune is processing your video.
              This can take a little while.
            </span>
          </div>
        </div>
      )}

      {outputUrl && !isEditing && (
        <section className="result-panel">
          <div className="result-heading">
            <div>
              <div className="eyebrow">
                COMPLETE
              </div>

              <h2>
                Your edited video is ready.
              </h2>
            </div>

            <a
              className="download-button"
              href={outputUrl}
              download="edited_video.mp4"
            >
              Download MP4 ↓
            </a>
          </div>

          <video
            className="result-video"
            src={outputUrl}
            controls
            autoPlay
          />
        </section>
      )}

      <footer>
        <span>RUNE</span>

        <span>
          Natural language → video edits
        </span>
      </footer>
    </main>
  );
}