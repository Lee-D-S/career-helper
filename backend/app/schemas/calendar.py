from datetime import datetime

from pydantic import BaseModel


class CalendarEventCreate(BaseModel):
    title: str
    description: str | None = None
    start_at: datetime
    end_at: datetime | None = None
    event_type: str = "task"
    source_type: str | None = None
    source_id: int | None = None


class CalendarEventRead(CalendarEventCreate):
    id: int


class CalendarEventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    event_type: str | None = None
    source_type: str | None = None
    source_id: int | None = None
