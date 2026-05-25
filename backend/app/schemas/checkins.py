from datetime import date

from pydantic import BaseModel


class DailyCheckInCreate(BaseModel):
    date: date
    actual_hours: float
    completed_work: str
    blockers: str | None = None


class DailyCheckInRead(DailyCheckInCreate):
    id: int


class WeeklyReviewCreate(BaseModel):
    weekly_plan_id: int
    blockers: str | None = None
    priority_adjustments: str | None = None
    score_changes: str | None = None
    summary: str | None = None


class WeeklyReviewRead(WeeklyReviewCreate):
    id: int
    completion_rate: float
