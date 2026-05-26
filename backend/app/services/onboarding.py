from datetime import date

from sqlalchemy import select
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


def _contains_any(text: str, keywords: list[str]) -> bool:
    normalized = text.lower()
    return any(keyword.lower() in normalized for keyword in keywords)


def estimate_initial_score(axis_name: str, payload: OnboardingInput) -> tuple[float, str | None]:
    notes = " ".join(
        [
            payload.primary_language or "",
            " ".join(payload.secondary_languages),
            payload.backend_experience or "",
            payload.db_experience or "",
            payload.infra_experience or "",
            payload.frontend_experience or "",
            payload.ai_data_experience or "",
            payload.coding_test_level or "",
            payload.raw_notes or "",
        ]
    )

    if axis_name == "프로그래밍 언어":
        if _contains_any(notes, ["python", "typescript", "javascript", "java", "파이썬", "타입스크립트", "자바"]):
            return 1.0, "온보딩에서 사용 언어 경험을 입력함"
    if axis_name == "백엔드/API":
        if _contains_any(notes, ["fastapi", "spring", "node", "api", "백엔드", "서버"]):
            return 1.0, "온보딩에서 백엔드/API 관련 경험을 입력함"
    if axis_name == "DB/SQL":
        if _contains_any(notes, ["postgres", "mysql", "sql", "db", "database"]):
            return 1.0, "온보딩에서 DB/SQL 경험을 입력함"
    if axis_name == "인프라/배포":
        if _contains_any(notes, ["aws", "linux", "docker", "배포", "인프라"]):
            return 1.0, "온보딩에서 인프라/배포 경험을 입력함"
    if axis_name == "코딩테스트":
        if _contains_any(notes, ["lv2", "level 2", "레벨 2", "프로그래머스 2"]):
            return 2.0, "온보딩에서 코딩테스트 Lv2 수준을 입력함"
        if _contains_any(notes, ["lv1", "level 1", "레벨 1", "프로그래머스"]):
            return 1.0, "온보딩에서 코딩테스트 경험을 입력함"
    if axis_name == "포트폴리오/프로젝트":
        if _contains_any(notes, ["프로젝트", "portfolio", "auto-invest", "공모전"]):
            return 2.0, "온보딩에서 프로젝트/공모전 경험을 입력함"
    if axis_name == "도메인 지식":
        if _contains_any(notes, ["금융", "투자", "거래", "블록체인", "코인", "선물", "saas"]):
            return 2.0, "온보딩에서 금융/거래 도메인 경험을 입력함"
    if axis_name == "서류/면접":
        if _contains_any(notes, ["이력서", "면접", "자소서"]):
            return 1.0, "온보딩에서 서류/면접 준비 경험을 입력함"
    if axis_name == "업무 관련 자격증" and payload.certificates:
        return 1.0, "온보딩에서 자격증 준비 항목을 입력함"
    if axis_name == "어학성적" and payload.language_scores:
        return 1.0, "온보딩에서 어학성적 항목을 입력함"

    return 0.0, None


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

    axes = await ensure_competency_axes(db)
    roles = payload.target_roles or DEFAULT_TRACKS
    existing_tracks_result = await db.execute(
        select(CareerTrack).where(CareerTrack.user_id == user_id).order_by(CareerTrack.priority, CareerTrack.id)
    )
    existing_tracks = list(existing_tracks_result.scalars())
    tracks_by_name = {track.name: track for track in existing_tracks}
    tracks: list[CareerTrack] = []
    for index, role in enumerate(roles, start=1):
        track = tracks_by_name.get(role)
        if track is None:
            track = CareerTrack(user_id=user_id, name=role, description=None)
            db.add(track)
        track.priority = index
        track.target_start_date = _parse_date(payload.target_application_start_date)
        tracks.append(track)

    await db.flush()

    for track in tracks:
        existing_scores_result = await db.execute(
            select(TrackCompetencyScore).where(TrackCompetencyScore.track_id == track.id)
        )
        scores_by_axis = {score.axis_id: score for score in existing_scores_result.scalars()}
        for axis in axes:
            initial_score, evidence = estimate_initial_score(axis.name, payload) if track.priority == 1 else (0.0, None)
            score = scores_by_axis.get(axis.id)
            if score is None:
                score = TrackCompetencyScore(
                    user_id=user_id,
                    track_id=track.id,
                    axis_id=axis.id,
                    target_score=3,
                )
                db.add(score)
                score.score = initial_score
                score.evidence = evidence
            score.weight = FINANCE_IT_WEIGHTS.get(axis.name, 0.1) if track.priority == 1 else 0.1

    await db.commit()
    return user_id, len(tracks), len(axes)
