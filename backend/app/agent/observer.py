import os

from app.agent.state import VideoAgentState
from app.video.ffmpeg import get_video_info


def observer_node(state: VideoAgentState):

    # Executor already failed so you don't need to go further
    if state.get("error"):
        return {
            "observation": (
                "Execution failed before successful output "
                "verification. "
                f"Error: {state['error']}"
            )
        }

    output_path = state["output_path"]

    if not os.path.exists(output_path):
        return {
            "error": "Output file was not created.",
            "observation": (
                "Execution appeared to finish, "
                "but the output file does not exist."
            ),
        }

    if os.path.getsize(output_path) == 0:
        return {
            "error": "Output file is empty.",
            "observation": (
                "Execution produced an empty output file."
            ),
        }

    try:
        output_info = get_video_info(output_path)

    except Exception as exc:
        return {
            "error": str(exc),
            "observation": (
                "Output file exists, but FFprobe could not "
                f"read it: {exc}"
            ),
        }

    return {
        "error": "",
        "observation": (
            "Execution successful. Output exists and "
            "FFprobe successfully analyzed it."
        ),
        "result": output_path,
        "video_info": output_info,
    }