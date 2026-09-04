from app.agent.planner import create_plan
from app.agent.state import VideoAgentState
from pathlib import Path
from app.video.plan_executor import execute_plan
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from app.agent.validator import validate_plan
from app.agent.analyzer import analyzer_node
from app.agent.observer import observer_node

MAX_ATTEMPTS = 3

def planner_node(
    state: VideoAgentState,
) -> dict:

    plan = create_plan(
        user_request=state["user_request"],
        video_info=state.get("video_info", {}),
        previous_error=state.get("error", ""),
        observation=state.get("observation", ""),
    )

    return {
        "plan": plan,
        "error" : ""
    }
    
def executor_node(
    state: VideoAgentState,
) -> dict:
    
    attempt = state.get("attempt", 0) + 1;

    plan = state["plan"]

    output_path = Path(
        state["output_path"]
    )

    input_path = Path(
        state["input_path"]
    )

    try:
        execute_plan(
            input_path=input_path,
            output_path=output_path,
            plan=plan,
        )

        return {
            "attempt": attempt,
            "error": "",
        }
        
    except Exception as exc:
        return {
            "attempt": attempt,
            "error": str(exc),
            "observation": (
                f"Execution failed with exception: {exc}"
            ),
        }
    
def validator_node(
    state: VideoAgentState,
) -> dict:

    return validate_plan(state)

def route_after_validation(
    state: VideoAgentState,
) -> str:

    if state.get("error"):
        return "replan"

    return "execute"

def route_after_observation(state: VideoAgentState):
    if not state.get("error"):
        return "success"

    if state.get("attempt", 0) >= MAX_ATTEMPTS:
        return "failed"

    return "replan"
    
def build_graph():

    graph = StateGraph(
        VideoAgentState
    )
    
    graph.add_node(
        "analyzer", 
        analyzer_node
    )

    graph.add_node(
        "planner",
        planner_node,
    )

    graph.add_node(
        "executor",
        executor_node,
    )

    graph.add_node(
        "validator",
        validator_node,
    )
    
    graph.add_node(
        "observer",
        observer_node
    )

    graph.add_edge(
        START,
        "analyzer",
    )
    
    graph.add_edge(
        "analyzer", 
        "planner"
    )

    graph.add_edge(
        "planner",
        "validator",
    )
    
    graph.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "execute": "executor",
            "replan": "planner",
        },
    )

    graph.add_edge(
        "executor",
        "observer",
    )
    
    graph.add_conditional_edges(
        "observer",
        route_after_observation,
        {
            "success" : END,
            "replan" : "planner",
            "failed" : END,
        }
    )
    


    return graph.compile()

