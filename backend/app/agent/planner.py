import os

from langchain_openai import ChatOpenAI

from app.video.models import EditingPlan
from app.agent.prompts import PLANNER_PROMPT
from dotenv import load_dotenv

load_dotenv()


llm = ChatOpenAI(
    model='openai/gpt-4o-mini',
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)


structured_llm = llm.with_structured_output(
    EditingPlan,
    method="function_calling"
)

def create_plan(user_request: str, video_info : dict, previous_error : str = "", observation : str = "") -> EditingPlan:

    prompt = PLANNER_PROMPT.format(
        user_request=user_request,
        video_info=video_info,
        previous_error=previous_error,
        observation=observation,
    )

    return structured_llm.invoke(prompt)