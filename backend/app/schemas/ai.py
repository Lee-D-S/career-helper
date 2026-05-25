from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AiSuggestionCreate(BaseModel):
    plan_type: str


class AiPlanDecisionUpdate(BaseModel):
    decision_status: str


class AiPlanRead(BaseModel):
    id: int
    plan_type: str
    raw_response: str | None
    parsed_json: dict[str, Any] | None
    user_explanation: str | None
    validation_status: str
    decision_status: str
    created_at: datetime
