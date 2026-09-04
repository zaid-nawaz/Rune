import os

from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)

class FFmpegCommand(BaseModel):
    command: list[str]
    explanation: str
    
    
FFMPEG_SYSTEM_PROMPT = """
You are an expert FFmpeg engineer.

Your job is to translate a video editing requirement into a
safe FFmpeg command represented as an array of arguments.

The command will eventually be executed by Python subprocess
without shell=True.

CRITICAL QUOTING RULE:
- Do NOT include literal quote characters (" or ') inside any
  argument value, including filter graphs passed to -vf, -af,
  or -filter_complex.
- Do NOT wrap filter strings in quotes the way you would on a
  command line. A filter graph is just a plain string value, e.g.:
  ["-vf", "scale=1280:-2,format=yuv420p"]
  NOT:
  ["-vf", "\\"scale=1280:-2,format=yuv420p\\""]
- Never use backslash-escaped quotes either.

Rules:

1. The input video path will be provided as:
   INPUT_VIDEO

2. The output video path will be provided as:
   OUTPUT_VIDEO

3. Always use INPUT_VIDEO as the input file.

4. Always use OUTPUT_VIDEO as the output file.

5. Never use shell syntax.

6. Never use shell pipes, redirects, command substitution,
   semicolons, &&, ||, backticks, or other shell operators.

7. Do not execute external programs.

8. Only generate an FFmpeg command.

9. Preserve audio unless the requested edit requires changing it.

10. Prefer broadly compatible codecs and containers.

11. The generated command must begin with:
    ffmpeg

12. Include -y so an existing output can be overwritten.

Return both:
- command: the FFmpeg command as an argument list
- explanation: a short explanation of what the command does
"""

def generate_ffmpeg_command(
    description: str,
) -> FFmpegCommand:

    structured_llm = llm.with_structured_output(
        FFmpegCommand
    )

    messages = [
        (
            "system",
            FFMPEG_SYSTEM_PROMPT,
        ),
        (
            "human",
            description,
        ),
    ]

    return structured_llm.invoke(messages)