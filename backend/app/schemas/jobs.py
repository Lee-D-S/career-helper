from datetime import date

from pydantic import BaseModel, Field


class JobPostingCreate(BaseModel):
    company_name: str | None = None
    position_title: str | None = None
    source_url: str | None = None
    raw_content: str | None = None
    deadline: date | None = None
    status: str = "saved"


class JobPostingRead(JobPostingCreate):
    id: int
    fit_score: float | None = None
    summary: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)


class JobPostingUpdate(BaseModel):
    company_name: str | None = None
    position_title: str | None = None
    source_url: str | None = None
    raw_content: str | None = None
    deadline: date | None = None
    status: str | None = None
