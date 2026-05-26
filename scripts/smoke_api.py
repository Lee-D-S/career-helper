from __future__ import annotations

import json
from typing import Any
from urllib.request import Request, urlopen


BASE_URL = "http://localhost:8000/api"


def request_json(method: str, path: str, body: dict[str, Any] | None = None) -> Any:
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = Request(
        f"{BASE_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urlopen(request, timeout=10) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else None


def main() -> None:
    onboarding = request_json(
        "POST",
        "/onboarding",
        {
            "user": {"name": "smoke-user", "school": "local", "major": "CS"},
            "target_roles": ["금융 IT 풀스택"],
            "weekday_available_hours": 2,
            "weekend_available_hours": 5,
            "primary_language": "Python",
            "backend_experience": "FastAPI toy project",
        },
    )

    dashboard = request_json("GET", "/dashboard")
    track_id = dashboard["readiness"][0]["id"]
    score_id = dashboard["readiness"][0]["scores"][0]["id"]
    score = request_json(
        "PATCH",
        f"/scores/{score_id}",
        {"score": 3, "target_score": 5, "evidence": "smoke update"},
    )

    roadmap = request_json(
        "POST",
        "/roadmaps",
        {
            "title": "Smoke Roadmap",
            "track_id": track_id,
            "start_date": "2026-05-26",
            "end_date": "2026-06-30",
            "items": [{"title": "Portfolio cleanup", "priority": 1, "status": "todo"}],
        },
    )

    weekly = request_json(
        "POST",
        "/weekly-plans",
        {
            "title": "Smoke Weekly Plan",
            "track_id": track_id,
            "week_start": "2026-05-25",
            "week_end": "2026-05-31",
            "tasks": [
                {
                    "title": "Write README proof",
                    "category": "portfolio",
                    "estimated_hours": 1.5,
                    "due_date": "2026-05-27",
                    "status": "todo",
                }
            ],
        },
    )

    task_id = weekly["tasks"][0]["id"]
    task = request_json("PATCH", f"/tasks/{task_id}", {"status": "done", "actual_hours": 1.25})
    checkin = request_json(
        "POST",
        "/daily-checkins",
        {
            "date": "2026-05-26",
            "actual_hours": 1.25,
            "completed_work": "Smoke check",
            "blockers": "none",
        },
    )
    review = request_json(
        "POST",
        "/weekly-reviews",
        {
            "weekly_plan_id": weekly["id"],
            "blockers": "none",
            "priority_adjustments": "keep",
            "score_changes": "none",
            "summary": "smoke review",
        },
    )

    ai_roadmap = request_json("POST", "/ai-suggestions", {"plan_type": "roadmap"})
    ai_accepted = request_json("PATCH", f"/ai-plans/{ai_roadmap['id']}", {"decision_status": "accepted"})

    job = request_json(
        "POST",
        "/job-postings",
        {
            "company_name": "Smoke Corp",
            "position_title": "Backend Intern",
            "source_url": "https://example.com/job",
            "raw_content": "Python FastAPI SQL",
            "deadline": "2026-06-15",
        },
    )
    job_analyzed = request_json("POST", f"/job-postings/{job['id']}/analyze", {})

    event = request_json(
        "POST",
        "/calendar-events",
        {
            "title": "Smoke Event",
            "description": "Manual event",
            "start_at": "2026-05-26T10:00:00",
            "end_at": "2026-05-26T11:00:00",
            "event_type": "manual",
        },
    )
    synced = request_json("POST", "/calendar-events/sync", {})
    request = Request(f"{BASE_URL}/calendar-events.ics", method="GET")
    with urlopen(request, timeout=10) as response:
        ics_status = response.status

    summary = {
        "onboarding": f"user={onboarding['user_id']},tracks={onboarding['track_count']},axes={onboarding['axis_count']}",
        "dashboard_track": dashboard["target_track"],
        "score_updated": score["id"],
        "roadmap": f"id={roadmap['id']},items={len(roadmap['items'])}",
        "weekly_plan": f"id={weekly['id']},tasks={len(weekly['tasks'])}",
        "task_status": task["status"],
        "checkin": checkin["id"],
        "review": f"id={review['id']},completion={review['completion_rate']}",
        "ai": f"id={ai_accepted['id']},applied={ai_accepted['applied_resource_type']}#{ai_accepted['applied_resource_id']}",
        "job": f"id={job_analyzed['id']},fit={job_analyzed['fit_score']},status={job_analyzed['status']}",
        "calendar": f"manual={event['id']},synced={len(synced)},icsStatus={ics_status}",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
