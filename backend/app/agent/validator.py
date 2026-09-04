from app.agent.state import VideoAgentState
from app.video.registry import OPERATIONS


def validate_plan(
    state: VideoAgentState,
) -> dict:

    plan = state["plan"]

    for operation in plan.operations:

        if operation.operation not in OPERATIONS and operation.operation != "custom_ffmpeg":
            return {
                "error": (
                    f"Unknown operation: "
                    f"{operation.operation}"
                )
            }

    return {
        "error": ""
    }