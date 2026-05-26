from datetime import date

from pydantic import BaseModel, Field


class RoadmapItemCreate(BaseModel):
    title: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    priority: int = 0
    status: str = "todo"


class RoadmapCreate(BaseModel):
    title: str
    track_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = "active"
    items: list[RoadmapItemCreate] = Field(default_factory=list)


class RoadmapItemRead(RoadmapItemCreate):
    id: int
    roadmap_id: int


class RoadmapRead(BaseModel):
    id: int
    title: str
    track_id: int | None
    start_date: date | None
    end_date: date | None
    status: str
    items: list[RoadmapItemRead]


class RoadmapUpdate(BaseModel):
    title: str | None = None
    track_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None


class RoadmapItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    priority: int | None = None
    status: str | None = None


class TaskCreate(BaseModel):
    title: str
    category: str = "general"
    description: str | None = None
    estimated_hours: float | None = None
    due_date: date | None = None
    reason: str | None = None
    status: str = "todo"


class WeeklyPlanCreate(BaseModel):
    title: str
    track_id: int | None = None
    week_start: date
    week_end: date
    status: str = "active"
    tasks: list[TaskCreate] = Field(default_factory=list)


class TaskRead(TaskCreate):
    id: int
    weekly_plan_id: int
    actual_hours: float | None = None


class WeeklyPlanRead(BaseModel):
    id: int
    title: str
    track_id: int | None
    week_start: date
    week_end: date
    status: str
    tasks: list[TaskRead]


class WeeklyPlanUpdate(BaseModel):
    title: str | None = None
    track_id: int | None = None
    week_start: date | None = None
    week_end: date | None = None
    status: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    description: str | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None
    due_date: date | None = None
    reason: str | None = None
    status: str | None = None
