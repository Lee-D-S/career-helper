from pydantic import BaseModel


class AxisScore(BaseModel):
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
