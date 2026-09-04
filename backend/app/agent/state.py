from typing import TypedDict

from app.video.models import EditingPlan


class VideoAgentState(TypedDict, total=False):
    user_request: str

    input_path: str
    output_path: str

    plan: EditingPlan

    error: str
    observation : str
    
    attempt : str

    result: str