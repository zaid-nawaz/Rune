from pydantic import BaseModel
from typing import Any


class EditingOperation(BaseModel):
    operation: str
    parameters: dict[str, Any] = {}


class EditingPlan(BaseModel):
    operations: list[EditingOperation]
    
