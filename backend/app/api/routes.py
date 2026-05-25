from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.models.ai_plan import AiPlan
from app.models.career import CareerTrack, CompetencyAxis, TrackCompetencyScore
from app.models.checkin import DailyCheckIn, WeeklyReview
from app.models.plan import Roadmap, RoadmapItem, Task, WeeklyPlan
from app.schemas.ai import AiPlanDecisionUpdate, AiPlanRead, AiSuggestionCreate
from app.schemas.checkins import DailyCheckInCreate, DailyCheckInRead, WeeklyReviewCreate, WeeklyReviewRead
from app.schemas.dashboard import AxisScore, DashboardSummary, ScoreUpdate, TrackReadiness
from app.schemas.onboarding import OnboardingInput, OnboardingResponse
from app.schemas.plans import (
    RoadmapCreate,
    RoadmapItemRead,
    RoadmapRead,
    TaskRead,
    TaskUpdate,
    WeeklyPlanCreate,
    WeeklyPlanRead,
)
from app.services.ai_provider import get_ai_provider
from app.services.onboarding import save_onboarding

router = APIRouter()


def _roadmap_read(roadmap: Roadmap, items: list[RoadmapItem]) -> RoadmapRead:
    return RoadmapRead(
        id=roadmap.id,
        title=roadmap.title,
        track_id=roadmap.track_id,
        start_date=roadmap.start_date,
        end_date=roadmap.end_date,
        status=roadmap.status,
        items=[
            RoadmapItemRead(
                id=item.id,
                roadmap_id=item.roadmap_id,
                title=item.title,
                description=item.description,
                start_date=item.start_date,
                end_date=item.end_date,
                priority=item.priority,
                status=item.status,
            )
            for item in items
        ],
    )


def _weekly_plan_read(plan: WeeklyPlan, tasks: list[Task]) -> WeeklyPlanRead:
    return WeeklyPlanRead(
        id=plan.id,
        title=plan.title,
        track_id=plan.track_id,
        week_start=plan.week_start,
        week_end=plan.week_end,
        status=plan.status,
        tasks=[
            TaskRead(
                id=task.id,
                weekly_plan_id=task.weekly_plan_id,
                title=task.title,
                category=task.category,
                description=task.description,
                estimated_hours=task.estimated_hours,
                actual_hours=task.actual_hours,
                status=task.status,
                due_date=task.due_date,
                reason=task.reason,
            )
            for task in tasks
        ],
    )


def _daily_checkin_read(checkin: DailyCheckIn) -> DailyCheckInRead:
    return DailyCheckInRead(
        id=checkin.id,
        date=checkin.date,
        actual_hours=checkin.actual_hours,
        completed_work=checkin.completed_work,
        blockers=checkin.blockers,
    )


def _weekly_review_read(review: WeeklyReview) -> WeeklyReviewRead:
    return WeeklyReviewRead(
        id=review.id,
        weekly_plan_id=review.weekly_plan_id,
        completion_rate=review.completion_rate,
        blockers=review.blockers,
        priority_adjustments=review.priority_adjustments,
        score_changes=review.score_changes,
        summary=review.summary,
    )


def _ai_plan_read(plan: AiPlan) -> AiPlanRead:
    parsed_json = plan.parsed_json or {}
    return AiPlanRead(
        id=plan.id,
        plan_type=plan.plan_type,
        raw_response=plan.raw_response,
        parsed_json=plan.parsed_json,
        user_explanation=plan.user_explanation,
        validation_status=plan.validation_status,
        decision_status=plan.decision_status,
        applied_resource_type=parsed_json.get("applied_resource_type") if isinstance(parsed_json, dict) else None,
        applied_resource_id=parsed_json.get("applied_resource_id") if isinstance(parsed_json, dict) else None,
        created_at=plan.created_at,
    )


async def _calculate_completion_rate(db: AsyncSession, weekly_plan_id: int) -> float:
    result = await db.execute(select(Task).where(Task.weekly_plan_id == weekly_plan_id))
    tasks = list(result.scalars())
    if not tasks:
        return 0
    done_count = sum(1 for task in tasks if task.status == "done")
    return round(done_count / len(tasks) * 100, 1)


async def _default_track_id(db: AsyncSession, user_id: int) -> int | None:
    result = await db.execute(select(CareerTrack).where(CareerTrack.user_id == user_id).order_by(CareerTrack.priority))
    track = result.scalars().first()
    return track.id if track else None


async def _apply_ai_plan(db: AsyncSession, plan: AiPlan) -> tuple[str | None, int | None]:
    if not isinstance(plan.parsed_json, dict):
        raise HTTPException(status_code=400, detail="AI plan has no parsed JSON")
    if plan.parsed_json.get("applied_resource_id"):
        return plan.parsed_json.get("applied_resource_type"), plan.parsed_json.get("applied_resource_id")

    today = date.today()
    track_id = await _default_track_id(db, plan.user_id)

    if plan.plan_type == "roadmap":
        roadmap = Roadmap(
            user_id=plan.user_id,
            track_id=track_id,
            title=str(plan.parsed_json.get("monthly_goal") or "AI 로드맵 제안"),
            start_date=today,
            end_date=today + timedelta(days=30),
            status="active",
            ai_plan_id=plan.id,
        )
        db.add(roadmap)
        await db.flush()

        for index, item in enumerate(plan.parsed_json.get("items", []), start=1):
            if not isinstance(item, dict):
                continue
            db.add(
                RoadmapItem(
                    roadmap_id=roadmap.id,
                    title=str(item.get("title") or f"로드맵 항목 {index}"),
                    description=item.get("reason"),
                    priority=int(item.get("priority") or index),
                    status="todo",
                )
            )

        plan.parsed_json = {
            **plan.parsed_json,
            "applied_resource_type": "roadmap",
            "applied_resource_id": roadmap.id,
        }
        return "roadmap", roadmap.id

    if plan.plan_type == "weekly_plan":
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        weekly_plan = WeeklyPlan(
            user_id=plan.user_id,
            track_id=track_id,
            week_start=week_start,
            week_end=week_end,
            title=str(plan.parsed_json.get("weekly_goal") or "AI 주간 계획 제안"),
            status="active",
            ai_plan_id=plan.id,
        )
        db.add(weekly_plan)
        await db.flush()

        for task_payload in plan.parsed_json.get("tasks", []):
            if not isinstance(task_payload, dict):
                continue
            db.add(
                Task(
                    weekly_plan_id=weekly_plan.id,
                    title=str(task_payload.get("title") or "작업"),
                    category=str(task_payload.get("category") or "general"),
                    description=task_payload.get("reason"),
                    estimated_hours=task_payload.get("estimated_hours"),
                    status="todo",
                )
            )

        plan.parsed_json = {
            **plan.parsed_json,
            "applied_resource_type": "weekly_plan",
            "applied_resource_id": weekly_plan.id,
        }
        return "weekly_plan", weekly_plan.id

    return None, None


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
                id=score.id,
                track_id=score.track_id,
                axis_id=score.axis_id,
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


@router.patch("/scores/{score_id}", response_model=AxisScore)
async def update_score(
    score_id: int,
    payload: ScoreUpdate,
    db: AsyncSession = Depends(get_db),
) -> AxisScore:
    user_id = get_settings().default_user_id
    score = await db.get(TrackCompetencyScore, score_id)
    if score is None or score.user_id != user_id:
        raise HTTPException(status_code=404, detail="Score not found")

    if payload.score < 0 or payload.score > 5:
        raise HTTPException(status_code=400, detail="score must be between 0 and 5")
    if payload.target_score is not None and (payload.target_score < 0 or payload.target_score > 5):
        raise HTTPException(status_code=400, detail="target_score must be between 0 and 5")

    score.score = payload.score
    if payload.target_score is not None:
        score.target_score = payload.target_score
    score.evidence = payload.evidence

    axis = await db.get(CompetencyAxis, score.axis_id)
    await db.commit()
    await db.refresh(score)

    if axis is None:
        raise HTTPException(status_code=500, detail="Axis not found")

    return AxisScore(
        id=score.id,
        track_id=score.track_id,
        axis_id=score.axis_id,
        axis=axis.name,
        score=score.score,
        target_score=score.target_score,
        weight=score.weight,
        evidence=score.evidence,
    )


@router.get("/roadmaps", response_model=list[RoadmapRead])
async def list_roadmaps(db: AsyncSession = Depends(get_db)) -> list[RoadmapRead]:
    user_id = get_settings().default_user_id
    result = await db.execute(select(Roadmap).where(Roadmap.user_id == user_id).order_by(Roadmap.start_date, Roadmap.id))
    roadmaps = list(result.scalars())
    response: list[RoadmapRead] = []
    for roadmap in roadmaps:
        items_result = await db.execute(
            select(RoadmapItem).where(RoadmapItem.roadmap_id == roadmap.id).order_by(RoadmapItem.priority, RoadmapItem.id)
        )
        response.append(_roadmap_read(roadmap, list(items_result.scalars())))
    return response


@router.post("/roadmaps", response_model=RoadmapRead)
async def create_roadmap(payload: RoadmapCreate, db: AsyncSession = Depends(get_db)) -> RoadmapRead:
    user_id = get_settings().default_user_id
    roadmap = Roadmap(
        user_id=user_id,
        track_id=payload.track_id,
        title=payload.title,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=payload.status,
    )
    db.add(roadmap)
    await db.flush()

    items: list[RoadmapItem] = []
    for item_payload in payload.items:
        item = RoadmapItem(
            roadmap_id=roadmap.id,
            title=item_payload.title,
            description=item_payload.description,
            start_date=item_payload.start_date,
            end_date=item_payload.end_date,
            priority=item_payload.priority,
            status=item_payload.status,
        )
        db.add(item)
        items.append(item)

    await db.commit()
    await db.refresh(roadmap)
    for item in items:
        await db.refresh(item)
    return _roadmap_read(roadmap, items)


@router.get("/weekly-plans", response_model=list[WeeklyPlanRead])
async def list_weekly_plans(db: AsyncSession = Depends(get_db)) -> list[WeeklyPlanRead]:
    user_id = get_settings().default_user_id
    result = await db.execute(
        select(WeeklyPlan).where(WeeklyPlan.user_id == user_id).order_by(WeeklyPlan.week_start.desc(), WeeklyPlan.id.desc())
    )
    plans = list(result.scalars())
    response: list[WeeklyPlanRead] = []
    for plan in plans:
        tasks_result = await db.execute(select(Task).where(Task.weekly_plan_id == plan.id).order_by(Task.due_date, Task.id))
        response.append(_weekly_plan_read(plan, list(tasks_result.scalars())))
    return response


@router.post("/weekly-plans", response_model=WeeklyPlanRead)
async def create_weekly_plan(payload: WeeklyPlanCreate, db: AsyncSession = Depends(get_db)) -> WeeklyPlanRead:
    user_id = get_settings().default_user_id
    plan = WeeklyPlan(
        user_id=user_id,
        track_id=payload.track_id,
        week_start=payload.week_start,
        week_end=payload.week_end,
        title=payload.title,
        status=payload.status,
    )
    db.add(plan)
    await db.flush()

    tasks: list[Task] = []
    for task_payload in payload.tasks:
        task = Task(
            weekly_plan_id=plan.id,
            title=task_payload.title,
            category=task_payload.category,
            description=task_payload.description,
            estimated_hours=task_payload.estimated_hours,
            status=task_payload.status,
            due_date=task_payload.due_date,
            reason=task_payload.reason,
        )
        db.add(task)
        tasks.append(task)

    await db.commit()
    await db.refresh(plan)
    for task in tasks:
        await db.refresh(task)
    return _weekly_plan_read(plan, tasks)


@router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(task_id: int, payload: TaskUpdate, db: AsyncSession = Depends(get_db)) -> TaskRead:
    user_id = get_settings().default_user_id
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    plan = await db.get(WeeklyPlan, task.weekly_plan_id)
    if plan is None or plan.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return TaskRead(
        id=task.id,
        weekly_plan_id=task.weekly_plan_id,
        title=task.title,
        category=task.category,
        description=task.description,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        status=task.status,
        due_date=task.due_date,
        reason=task.reason,
    )


@router.get("/daily-checkins", response_model=list[DailyCheckInRead])
async def list_daily_checkins(db: AsyncSession = Depends(get_db)) -> list[DailyCheckInRead]:
    user_id = get_settings().default_user_id
    result = await db.execute(
        select(DailyCheckIn).where(DailyCheckIn.user_id == user_id).order_by(DailyCheckIn.date.desc(), DailyCheckIn.id.desc())
    )
    return [_daily_checkin_read(checkin) for checkin in result.scalars()]


@router.post("/daily-checkins", response_model=DailyCheckInRead)
async def create_daily_checkin(payload: DailyCheckInCreate, db: AsyncSession = Depends(get_db)) -> DailyCheckInRead:
    user_id = get_settings().default_user_id
    checkin = DailyCheckIn(
        user_id=user_id,
        date=payload.date,
        actual_hours=payload.actual_hours,
        completed_work=payload.completed_work,
        blockers=payload.blockers,
    )
    db.add(checkin)
    await db.commit()
    await db.refresh(checkin)
    return _daily_checkin_read(checkin)


@router.get("/weekly-reviews", response_model=list[WeeklyReviewRead])
async def list_weekly_reviews(db: AsyncSession = Depends(get_db)) -> list[WeeklyReviewRead]:
    user_id = get_settings().default_user_id
    result = await db.execute(
        select(WeeklyReview).where(WeeklyReview.user_id == user_id).order_by(WeeklyReview.created_at.desc(), WeeklyReview.id.desc())
    )
    return [_weekly_review_read(review) for review in result.scalars()]


@router.post("/weekly-reviews", response_model=WeeklyReviewRead)
async def create_weekly_review(payload: WeeklyReviewCreate, db: AsyncSession = Depends(get_db)) -> WeeklyReviewRead:
    user_id = get_settings().default_user_id
    plan = await db.get(WeeklyPlan, payload.weekly_plan_id)
    if plan is None or plan.user_id != user_id:
        raise HTTPException(status_code=404, detail="Weekly plan not found")

    existing = await db.scalar(select(WeeklyReview).where(WeeklyReview.weekly_plan_id == payload.weekly_plan_id))
    completion_rate = await _calculate_completion_rate(db, payload.weekly_plan_id)
    if existing is None:
        existing = WeeklyReview(user_id=user_id, weekly_plan_id=payload.weekly_plan_id)
        db.add(existing)

    existing.completion_rate = completion_rate
    existing.blockers = payload.blockers
    existing.priority_adjustments = payload.priority_adjustments
    existing.score_changes = payload.score_changes
    existing.summary = payload.summary

    await db.commit()
    await db.refresh(existing)
    return _weekly_review_read(existing)


@router.get("/ai-plans", response_model=list[AiPlanRead])
async def list_ai_plans(db: AsyncSession = Depends(get_db)) -> list[AiPlanRead]:
    user_id = get_settings().default_user_id
    result = await db.execute(select(AiPlan).where(AiPlan.user_id == user_id).order_by(AiPlan.created_at.desc(), AiPlan.id.desc()))
    return [_ai_plan_read(plan) for plan in result.scalars()]


@router.post("/ai-suggestions", response_model=AiPlanRead)
async def create_ai_suggestion(payload: AiSuggestionCreate, db: AsyncSession = Depends(get_db)) -> AiPlanRead:
    user_id = get_settings().default_user_id
    provider = get_ai_provider()

    if payload.plan_type == "roadmap":
        parsed = await provider.generate_roadmap()
        explanation = "현재 목표 직무와 부족 역량을 기준으로 로드맵 초안을 생성했습니다."
    elif payload.plan_type == "weekly_plan":
        parsed = await provider.generate_weekly_plan()
        explanation = "이번 주 실행 가능한 산출물 중심으로 주간 계획 초안을 생성했습니다."
    elif payload.plan_type == "weekly_review":
        parsed = await provider.generate_weekly_review()
        explanation = "주간 회고에서 확인해야 할 기준과 요약 초안을 생성했습니다."
    elif payload.plan_type == "job_posting":
        parsed = await provider.analyze_job_posting()
        explanation = "공고 분석 초안을 생성했습니다."
    else:
        raise HTTPException(status_code=400, detail="Unsupported suggestion type")

    plan = AiPlan(
        user_id=user_id,
        plan_type=payload.plan_type,
        raw_response=str(parsed),
        parsed_json=parsed,
        user_explanation=explanation,
        validation_status="valid",
        decision_status="suggested",
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return _ai_plan_read(plan)


@router.patch("/ai-plans/{plan_id}", response_model=AiPlanRead)
async def update_ai_plan_decision(
    plan_id: int,
    payload: AiPlanDecisionUpdate,
    db: AsyncSession = Depends(get_db),
) -> AiPlanRead:
    user_id = get_settings().default_user_id
    if payload.decision_status not in {"suggested", "accepted", "edited", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid decision_status")

    plan = await db.get(AiPlan, plan_id)
    if plan is None or plan.user_id != user_id:
        raise HTTPException(status_code=404, detail="AI plan not found")

    plan.decision_status = payload.decision_status
    if payload.decision_status == "accepted":
        await _apply_ai_plan(db, plan)
    await db.commit()
    await db.refresh(plan)
    return _ai_plan_read(plan)
