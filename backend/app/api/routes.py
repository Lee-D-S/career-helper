from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.models.career import CareerTrack, CompetencyAxis, TrackCompetencyScore
from app.schemas.dashboard import AxisScore, DashboardSummary, TrackReadiness
from app.schemas.onboarding import OnboardingInput, OnboardingResponse
from app.services.onboarding import save_onboarding

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/onboarding", response_model=OnboardingResponse)
async def create_onboarding(payload: OnboardingInput, db: AsyncSession = Depends(get_db)) -> OnboardingResponse:
    user_id, track_count, axis_count = await save_onboarding(db, payload)
    return OnboardingResponse(user_id=user_id, track_count=track_count, axis_count=axis_count)


@router.get("/dashboard", response_model=DashboardSummary)
async def dashboard(db: AsyncSession = Depends(get_db)) -> DashboardSummary:
    user_id = get_settings().default_user_id
    tracks_result = await db.execute(
        select(CareerTrack).where(CareerTrack.user_id == user_id).order_by(CareerTrack.priority)
    )
    tracks = list(tracks_result.scalars())

    readiness: list[TrackReadiness] = []
    all_scores: list[AxisScore] = []
    for track in tracks:
        rows = await db.execute(
            select(TrackCompetencyScore, CompetencyAxis)
            .join(CompetencyAxis, CompetencyAxis.id == TrackCompetencyScore.axis_id)
            .where(TrackCompetencyScore.track_id == track.id)
            .order_by(CompetencyAxis.id)
        )
        axis_scores: list[AxisScore] = []
        weighted_total = 0.0
        weight_total = 0.0
        for score, axis in rows:
            item = AxisScore(
                axis=axis.name,
                score=score.score,
                target_score=score.target_score,
                weight=score.weight,
                evidence=score.evidence,
            )
            axis_scores.append(item)
            all_scores.append(item)
            weighted_total += score.score * score.weight
            weight_total += score.weight

        readiness.append(
            TrackReadiness(
                id=track.id,
                name=track.name,
                priority=track.priority,
                weighted_score=round(weighted_total / weight_total, 2) if weight_total else 0,
                scores=axis_scores,
            )
        )

    weakest_axes = sorted(all_scores, key=lambda item: (item.score, -item.weight))[:3]
    return DashboardSummary(
        target_track=tracks[0].name if tracks else None,
        readiness=readiness,
        weakest_axes=weakest_axes,
    )
