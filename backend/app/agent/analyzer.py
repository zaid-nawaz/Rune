from app.agent.state import VideoAgentState
from app.video.ffmpeg import get_video_info


def analyzer_node(state: VideoAgentState):
    input_path = state["input_path"]

    video_info = get_video_info(input_path)

    return {
        "video_info": video_info,
        "attempt": 0,
        "error": "",
        "observation": "",
    }