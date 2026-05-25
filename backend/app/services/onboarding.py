from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.career import CareerTrack, TrackCompetencyScore
from app.models.onboarding import OnboardingProfile
from app.models.user import User
from app.schemas.onboarding import OnboardingInput
from app.services.seed import FINANCE_IT_WEIGHTS, ensure_competency_axes

DEFAULT_TRACKS = ["금융 IT 풀스택", "백엔드/서버", "AI", "데이터"]


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


async def save_onboarding(db: AsyncSession, payload: OnboardingInput) -> tuple[int, int, int]:
    settings = get_settings()
    user_id = settings.default_user_id

    user = await db.get(User, user_id)
    if user is None:
        user = User(id=user_id)
        db.add(user)

    user.name = payload.user.name
    user.school = payload.user.school
    user.major = payload.user.major
    user.current_semester = payload.user.current_semester
    user.expected_graduation_date = _parse_date(payload.user.expected_graduation_date)
    user.overall_gpa = payload.user.overall_gpa
    user.major_gpa = payload.user.major_gpa
    user.total_credits = payload.user.total_credits

    existing_profile = await db.scalar(select(OnboardingProfile).where(OnboardingProfile.user_id == user_id))
    if existing_profile is None:
        existing_profile = OnboardingProfile(user_id=user_id)
        db.add(existing_profile)

    for field, value in payload.model_dump(exclude={"user"}).items():
        setattr(existing_profile, field, value)

    await db.execute(delete(TrackCompetencyScore).where(TrackCompetencyScore.user_id == user_id))
    await db.execute(delete(CareerTrack).where(CareerTrack.user_id == user_id))

    axes = await ensure_competency_axes(db)
    roles = payload.target_roles or DEFAULT_TRACKS
    tracks: list[CareerTrack] = []
    for index, role in enumerate(roles, start=1):
        track = CareerTrack(
            user_id=user_id,
            name=role,
            priority=index,
            description=None,
            target_start_date=_parse_date(payload.target_application_start_date),
        )
        db.add(track)
        tracks.append(track)

    await db.flush()

    for track in tracks:
        for axis in axes:
            db.add(
                TrackCompetencyScore(
                    user_id=user_id,
                    track_id=track.id,
                    axis_id=axis.id,
                    score=0,
                    target_score=3,
                    weight=FINANCE_IT_WEIGHTS.get(axis.name, 0.1) if track.priority == 1 else 0.1,
                )
            )

    await db.commit()
    return user_id, len(tracks), len(axes)
