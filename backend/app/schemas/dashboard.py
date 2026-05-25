from pydantic import BaseModel


class AxisScore(BaseModel):
    id: int
    track_id: int
    axis_id: int
    axis: str
    score: float
    target_score: float
    weight: float
    evidence: str | None = None


class TrackReadiness(BaseModel):
    id: int
    name: str
    priority: int
    weighted_score: float
    scores: list[AxisScore]


class DashboardSummary(BaseModel):
    target_track: str | None
    readiness: list[TrackReadiness]
    weakest_axes: list[AxisScore]


class ScoreUpdate(BaseModel):
    score: float
    target_score: float | None = None
    evidence: str | None = None
