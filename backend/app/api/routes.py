from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy import delete as sqla_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.models.ai_plan import AiPlan
from app.models.calendar import CalendarEvent
from app.models.career import CareerTrack, CompetencyAxis, TrackCompetencyScore
from app.models.checkin import DailyCheckIn, WeeklyReview
from app.models.job import JobPosting
from app.models.plan import Roadmap, RoadmapItem, Task, WeeklyPlan
from app.schemas.ai import AiPlanDecisionUpdate, AiPlanRead, AiSuggestionCreate
from app.schemas.calendar import CalendarEventCreate, CalendarEventRead, CalendarEventUpdate
from app.schemas.checkins import DailyCheckInCreate, DailyCheckInRead, WeeklyReviewCreate, WeeklyReviewRead
from app.schemas.dashboard import AxisScore, DashboardSummary, ScoreUpdate, TrackReadiness
from app.schemas.jobs import JobPostingCreate, JobPostingRead, JobPostingUpdate
from app.schemas.onboarding import OnboardingInput, OnboardingResponse
from app.schemas.plans import (
    RoadmapCreate,
    RoadmapItemRead,
    RoadmapItemUpdate,
    RoadmapRead,
    RoadmapUpdate,
    TaskRead,
    TaskUpdate,
    WeeklyPlanCreate,
    WeeklyPlanRead,
    WeeklyPlanUpdate,
)
from app.services.ai_provider import AIProviderError, MockProvider, get_ai_provider
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
        ai_plan_id=roadmap.ai_plan_id,
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
        ai_plan_id=plan.ai_plan_id,
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


def _job_posting_read(job: JobPosting) -> JobPostingRead:
    return JobPostingRead(
        id=job.id,
        company_name=job.company_name,
        position_title=job.position_title,
        source_url=job.source_url,
        raw_content=job.raw_content,
        deadline=job.deadline,
        status=job.status,
        fit_score=job.fit_score,
        summary=job.summary,
        required_skills=job.required_skills or [],
        recommended_actions=job.recommended_actions or [],
    )


def _calendar_event_read(event: CalendarEvent) -> CalendarEventRead:
    return CalendarEventRead(
        id=event.id,
        title=event.title,
        description=event.description,
        start_at=event.start_at,
        end_at=event.end_at,
        event_type=event.event_type,
        source_type=event.source_type,
        source_id=event.source_id,
    )


def _ics_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def _ics_datetime(value) -> str:
    return value.strftime("%Y%m%dT%H%M%S")


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

    if plan.plan_type == "weekly_review":
        latest_plan = await db.scalar(
            select(WeeklyPlan)
            .where(WeeklyPlan.user_id == plan.user_id)
            .order_by(WeeklyPlan.week_start.desc(), WeeklyPlan.id.desc())
        )
        if latest_plan is None:
            raise HTTPException(status_code=400, detail="Weekly plan is required before applying a weekly review")

        review = await db.scalar(select(WeeklyReview).where(WeeklyReview.weekly_plan_id == latest_plan.id))
        if review is None:
            review = WeeklyReview(user_id=plan.user_id, weekly_plan_id=latest_plan.id)
            db.add(review)

        questions = plan.parsed_json.get("review_questions", [])
        if isinstance(questions, list):
            priority_adjustments = "\n".join(str(question) for question in questions)
        else:
            priority_adjustments = str(questions) if questions else None

        review.completion_rate = await _calculate_completion_rate(db, latest_plan.id)
        review.summary = str(plan.parsed_json.get("summary") or "AI 주간 회고 초안")
        review.priority_adjustments = priority_adjustments

        await db.flush()
        plan.parsed_json = {
            **plan.parsed_json,
            "applied_resource_type": "weekly_review",
            "applied_resource_id": review.id,
        }
        return "weekly_review", review.id

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


@router.patch("/roadmaps/{roadmap_id}", response_model=RoadmapRead)
async def update_roadmap(roadmap_id: int, payload: RoadmapUpdate, db: AsyncSession = Depends(get_db)) -> RoadmapRead:
    user_id = get_settings().default_user_id
    roadmap = await db.get(Roadmap, roadmap_id)
    if roadmap is None or roadmap.user_id != user_id:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(roadmap, field, value)

    await db.commit()
    await db.refresh(roadmap)
    items_result = await db.execute(
        select(RoadmapItem).where(RoadmapItem.roadmap_id == roadmap.id).order_by(RoadmapItem.priority, RoadmapItem.id)
    )
    return _roadmap_read(roadmap, list(items_result.scalars()))


@router.delete("/roadmaps/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_roadmap(roadmap_id: int, db: AsyncSession = Depends(get_db)) -> Response:
    user_id = get_settings().default_user_id
    roadmap = await db.get(Roadmap, roadmap_id)
    if roadmap is None or roadmap.user_id != user_id:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    await db.execute(sqla_delete(RoadmapItem).where(RoadmapItem.roadmap_id == roadmap.id))
    await db.delete(roadmap)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/roadmap-items/{item_id}", response_model=RoadmapItemRead)
async def update_roadmap_item(
    item_id: int,
    payload: RoadmapItemUpdate,
    db: AsyncSession = Depends(get_db),
) -> RoadmapItemRead:
    user_id = get_settings().default_user_id
    item = await db.get(RoadmapItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Roadmap item not found")
    roadmap = await db.get(Roadmap, item.roadmap_id)
    if roadmap is None or roadmap.user_id != user_id:
        raise HTTPException(status_code=404, detail="Roadmap item not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)
    return RoadmapItemRead(
        id=item.id,
        roadmap_id=item.roadmap_id,
        title=item.title,
        description=item.description,
        start_date=item.start_date,
        end_date=item.end_date,
        priority=item.priority,
        status=item.status,
    )


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


@router.patch("/weekly-plans/{plan_id}", response_model=WeeklyPlanRead)
async def update_weekly_plan(plan_id: int, payload: WeeklyPlanUpdate, db: AsyncSession = Depends(get_db)) -> WeeklyPlanRead:
    user_id = get_settings().default_user_id
    plan = await db.get(WeeklyPlan, plan_id)
    if plan is None or plan.user_id != user_id:
        raise HTTPException(status_code=404, detail="Weekly plan not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)

    await db.commit()
    await db.refresh(plan)
    tasks_result = await db.execute(select(Task).where(Task.weekly_plan_id == plan.id).order_by(Task.due_date, Task.id))
    return _weekly_plan_read(plan, list(tasks_result.scalars()))


@router.delete("/weekly-plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weekly_plan(plan_id: int, db: AsyncSession = Depends(get_db)) -> Response:
    user_id = get_settings().default_user_id
    plan = await db.get(WeeklyPlan, plan_id)
    if plan is None or plan.user_id != user_id:
        raise HTTPException(status_code=404, detail="Weekly plan not found")

    task_ids_result = await db.execute(select(Task.id).where(Task.weekly_plan_id == plan.id))
    task_ids = list(task_ids_result.scalars())
    if task_ids:
        await db.execute(
            sqla_delete(CalendarEvent).where(CalendarEvent.source_type == "task", CalendarEvent.source_id.in_(task_ids))
        )
    await db.execute(sqla_delete(WeeklyReview).where(WeeklyReview.weekly_plan_id == plan.id))
    await db.execute(sqla_delete(Task).where(Task.weekly_plan_id == plan.id))
    await db.delete(plan)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
    try:
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
        raw_response = str(parsed)
        validation_status = "valid"
    except AIProviderError as exc:
        if payload.plan_type not in {"roadmap", "weekly_plan", "weekly_review", "job_posting"}:
            raise HTTPException(status_code=400, detail="Unsupported suggestion type") from exc
        parsed = {"error": str(exc), "manual_fallback": True}
        raw_response = str(exc)
        explanation = "AI 제안 생성에 실패했습니다. 수동 작성 화면에서 계속 진행할 수 있습니다."
        validation_status = "invalid"

    plan = AiPlan(
        user_id=user_id,
        plan_type=payload.plan_type,
        raw_response=raw_response,
        parsed_json=parsed,
        user_explanation=explanation,
        validation_status=validation_status,
        decision_status="suggested",
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return _ai_plan_read(plan)


@router.get("/job-postings", response_model=list[JobPostingRead])
async def list_job_postings(db: AsyncSession = Depends(get_db)) -> list[JobPostingRead]:
    user_id = get_settings().default_user_id
    result = await db.execute(
        select(JobPosting).where(JobPosting.user_id == user_id).order_by(JobPosting.deadline, JobPosting.id.desc())
    )
    return [_job_posting_read(job) for job in result.scalars()]


@router.post("/job-postings", response_model=JobPostingRead)
async def create_job_posting(payload: JobPostingCreate, db: AsyncSession = Depends(get_db)) -> JobPostingRead:
    user_id = get_settings().default_user_id
    job = JobPosting(
        user_id=user_id,
        company_name=payload.company_name,
        position_title=payload.position_title,
        source_url=payload.source_url,
        raw_content=payload.raw_content,
        deadline=payload.deadline,
        status=payload.status,
        required_skills=[],
        recommended_actions=[],
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return _job_posting_read(job)


@router.patch("/job-postings/{job_id}", response_model=JobPostingRead)
async def update_job_posting(job_id: int, payload: JobPostingUpdate, db: AsyncSession = Depends(get_db)) -> JobPostingRead:
    user_id = get_settings().default_user_id
    job = await db.get(JobPosting, job_id)
    if job is None or job.user_id != user_id:
        raise HTTPException(status_code=404, detail="Job posting not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    await db.commit()
    await db.refresh(job)
    return _job_posting_read(job)


@router.delete("/job-postings/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_posting(job_id: int, db: AsyncSession = Depends(get_db)) -> Response:
    user_id = get_settings().default_user_id
    job = await db.get(JobPosting, job_id)
    if job is None or job.user_id != user_id:
        raise HTTPException(status_code=404, detail="Job posting not found")

    await db.delete(job)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/job-postings/{job_id}/analyze", response_model=JobPostingRead)
async def analyze_job_posting(job_id: int, db: AsyncSession = Depends(get_db)) -> JobPostingRead:
    user_id = get_settings().default_user_id
    job = await db.get(JobPosting, job_id)
    if job is None or job.user_id != user_id:
        raise HTTPException(status_code=404, detail="Job posting not found")

    try:
        provider = get_ai_provider()
        analysis = await provider.analyze_job_posting(job.raw_content or job.source_url)
    except AIProviderError:
        analysis = await MockProvider().analyze_job_posting(job.raw_content or job.source_url)
    job.summary = analysis.get("summary")
    job.fit_score = analysis.get("fit_score")
    job.required_skills = analysis.get("required_skills", [])
    job.recommended_actions = analysis.get("recommended_actions", [])
    job.status = "ready"

    await db.commit()
    await db.refresh(job)
    return _job_posting_read(job)


@router.get("/calendar-events", response_model=list[CalendarEventRead])
async def list_calendar_events(db: AsyncSession = Depends(get_db)) -> list[CalendarEventRead]:
    user_id = get_settings().default_user_id
    result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.user_id == user_id).order_by(CalendarEvent.start_at, CalendarEvent.id)
    )
    return [_calendar_event_read(event) for event in result.scalars()]


@router.post("/calendar-events", response_model=CalendarEventRead)
async def create_calendar_event(payload: CalendarEventCreate, db: AsyncSession = Depends(get_db)) -> CalendarEventRead:
    user_id = get_settings().default_user_id
    event = CalendarEvent(
        user_id=user_id,
        title=payload.title,
        description=payload.description,
        start_at=payload.start_at,
        end_at=payload.end_at,
        event_type=payload.event_type,
        source_type=payload.source_type,
        source_id=payload.source_id,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return _calendar_event_read(event)


@router.patch("/calendar-events/{event_id}", response_model=CalendarEventRead)
async def update_calendar_event(
    event_id: int,
    payload: CalendarEventUpdate,
    db: AsyncSession = Depends(get_db),
) -> CalendarEventRead:
    user_id = get_settings().default_user_id
    event = await db.get(CalendarEvent, event_id)
    if event is None or event.user_id != user_id:
        raise HTTPException(status_code=404, detail="Calendar event not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)
    return _calendar_event_read(event)


@router.delete("/calendar-events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar_event(event_id: int, db: AsyncSession = Depends(get_db)) -> Response:
    user_id = get_settings().default_user_id
    event = await db.get(CalendarEvent, event_id)
    if event is None or event.user_id != user_id:
        raise HTTPException(status_code=404, detail="Calendar event not found")

    await db.delete(event)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/calendar-events/sync", response_model=list[CalendarEventRead])
async def sync_calendar_events(db: AsyncSession = Depends(get_db)) -> list[CalendarEventRead]:
    user_id = get_settings().default_user_id
    created: list[CalendarEvent] = []

    tasks_result = await db.execute(
        select(Task, WeeklyPlan)
        .join(WeeklyPlan, WeeklyPlan.id == Task.weekly_plan_id)
        .where(WeeklyPlan.user_id == user_id, Task.due_date.is_not(None))
    )
    for task, plan in tasks_result:
        existing = await db.scalar(
            select(CalendarEvent).where(
                CalendarEvent.user_id == user_id,
                CalendarEvent.source_type == "task",
                CalendarEvent.source_id == task.id,
            )
        )
        if existing is not None:
            continue
        event = CalendarEvent(
            user_id=user_id,
            title=task.title,
            description=task.reason or task.description,
            start_at=datetime.combine(task.due_date, time(hour=9)),
            end_at=None,
            event_type="task",
            source_type="task",
            source_id=task.id,
        )
        db.add(event)
        created.append(event)

    jobs_result = await db.execute(select(JobPosting).where(JobPosting.user_id == user_id, JobPosting.deadline.is_not(None)))
    for job in jobs_result.scalars():
        existing = await db.scalar(
            select(CalendarEvent).where(
                CalendarEvent.user_id == user_id,
                CalendarEvent.source_type == "job_posting",
                CalendarEvent.source_id == job.id,
            )
        )
        if existing is not None:
            continue
        title = f"{job.company_name or '공고'} 마감"
        event = CalendarEvent(
            user_id=user_id,
            title=title,
            description=job.position_title,
            start_at=datetime.combine(job.deadline, time(hour=9)),
            end_at=None,
            event_type="job_deadline",
            source_type="job_posting",
            source_id=job.id,
        )
        db.add(event)
        created.append(event)

    await db.commit()
    for event in created:
        await db.refresh(event)
    return [_calendar_event_read(event) for event in created]


@router.get("/calendar-events.ics")
async def export_calendar_events(db: AsyncSession = Depends(get_db)) -> Response:
    user_id = get_settings().default_user_id
    result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.user_id == user_id).order_by(CalendarEvent.start_at, CalendarEvent.id)
    )
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Career Helper//KO"]
    for event in result.scalars():
        end_at = event.end_at or event.start_at
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:career-helper-{event.id}@local",
                f"DTSTAMP:{_ics_datetime(event.created_at)}",
                f"DTSTART:{_ics_datetime(event.start_at)}",
                f"DTEND:{_ics_datetime(end_at)}",
                f"SUMMARY:{_ics_escape(event.title)}",
                f"DESCRIPTION:{_ics_escape(event.description or '')}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    return Response(
        "\r\n".join(lines),
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="career-helper-calendar.ics"'},
    )


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

    if payload.parsed_json is not None:
        plan.parsed_json = payload.parsed_json
        plan.raw_response = str(payload.parsed_json)
        plan.validation_status = "valid"
    if payload.user_explanation is not None:
        plan.user_explanation = payload.user_explanation

    plan.decision_status = payload.decision_status
    if payload.decision_status == "accepted":
        if plan.validation_status != "valid":
            raise HTTPException(status_code=400, detail="Invalid AI plan cannot be accepted")
        await _apply_ai_plan(db, plan)
    await db.commit()
    await db.refresh(plan)
    return _ai_plan_read(plan)
