"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("school", sa.String(length=120), nullable=True),
        sa.Column("major", sa.String(length=120), nullable=True),
        sa.Column("current_semester", sa.String(length=30), nullable=True),
        sa.Column("expected_graduation_date", sa.Date(), nullable=True),
        sa.Column("overall_gpa", sa.Float(), nullable=True),
        sa.Column("major_gpa", sa.Float(), nullable=True),
        sa.Column("total_credits", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ai_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_type", sa.String(length=50), nullable=False),
        sa.Column("raw_response", sa.Text(), nullable=True),
        sa.Column("parsed_json", sa.JSON(), nullable=True),
        sa.Column("user_explanation", sa.Text(), nullable=True),
        sa.Column("validation_status", sa.String(length=30), nullable=False),
        sa.Column("decision_status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_plans_user_id"), "ai_plans", ["user_id"])
    op.create_table(
        "career_tracks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_start_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_career_tracks_user_id"), "career_tracks", ["user_id"])
    op.create_table(
        "competency_axes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "onboarding_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("target_roles", sa.JSON(), nullable=False),
        sa.Column("target_application_start_date", sa.Text(), nullable=True),
        sa.Column("desired_employment_date", sa.Text(), nullable=True),
        sa.Column("weekday_available_hours", sa.Float(), nullable=True),
        sa.Column("weekend_available_hours", sa.Float(), nullable=True),
        sa.Column("primary_language", sa.Text(), nullable=True),
        sa.Column("secondary_languages", sa.JSON(), nullable=False),
        sa.Column("backend_experience", sa.Text(), nullable=True),
        sa.Column("db_experience", sa.Text(), nullable=True),
        sa.Column("infra_experience", sa.Text(), nullable=True),
        sa.Column("frontend_experience", sa.Text(), nullable=True),
        sa.Column("ai_data_experience", sa.Text(), nullable=True),
        sa.Column("coding_test_level", sa.Text(), nullable=True),
        sa.Column("certificates", sa.JSON(), nullable=False),
        sa.Column("language_scores", sa.JSON(), nullable=False),
        sa.Column("preferred_industries", sa.JSON(), nullable=False),
        sa.Column("avoided_roles", sa.JSON(), nullable=False),
        sa.Column("constraints", sa.Text(), nullable=True),
        sa.Column("raw_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_onboarding_profiles_user_id"), "onboarding_profiles", ["user_id"])
    op.create_table(
        "track_competency_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=False),
        sa.Column("axis_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("target_score", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["axis_id"], ["competency_axes.id"]),
        sa.ForeignKeyConstraint(["track_id"], ["career_tracks.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("track_id", "axis_id", name="uq_track_axis"),
    )
    op.create_index(op.f("ix_track_competency_scores_axis_id"), "track_competency_scores", ["axis_id"])
    op.create_index(op.f("ix_track_competency_scores_track_id"), "track_competency_scores", ["track_id"])
    op.create_index(op.f("ix_track_competency_scores_user_id"), "track_competency_scores", ["user_id"])
    op.create_table(
        "roadmaps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("ai_plan_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["ai_plan_id"], ["ai_plans.id"]),
        sa.ForeignKeyConstraint(["track_id"], ["career_tracks.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_roadmaps_user_id"), "roadmaps", ["user_id"])
    op.create_table(
        "roadmap_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("roadmap_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["roadmap_id"], ["roadmaps.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_roadmap_items_roadmap_id"), "roadmap_items", ["roadmap_id"])
    op.create_table(
        "weekly_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=True),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("week_end", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("ai_plan_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["ai_plan_id"], ["ai_plans.id"]),
        sa.ForeignKeyConstraint(["track_id"], ["career_tracks.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_weekly_plans_user_id"), "weekly_plans", ["user_id"])
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("weekly_plan_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("estimated_hours", sa.Float(), nullable=True),
        sa.Column("actual_hours", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["weekly_plan_id"], ["weekly_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_weekly_plan_id"), "tasks", ["weekly_plan_id"])
    op.create_table(
        "daily_checkins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("actual_hours", sa.Float(), nullable=False),
        sa.Column("completed_work", sa.Text(), nullable=False),
        sa.Column("blockers", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_daily_checkins_date"), "daily_checkins", ["date"])
    op.create_index(op.f("ix_daily_checkins_user_id"), "daily_checkins", ["user_id"])
    op.create_table(
        "weekly_reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("weekly_plan_id", sa.Integer(), nullable=False),
        sa.Column("completion_rate", sa.Float(), nullable=False),
        sa.Column("blockers", sa.Text(), nullable=True),
        sa.Column("priority_adjustments", sa.Text(), nullable=True),
        sa.Column("score_changes", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["weekly_plan_id"], ["weekly_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("weekly_plan_id"),
    )
    op.create_index(op.f("ix_weekly_reviews_user_id"), "weekly_reviews", ["user_id"])
    op.create_table(
        "job_postings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(length=120), nullable=True),
        sa.Column("position_title", sa.String(length=160), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("raw_content", sa.Text(), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("fit_score", sa.Float(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("required_skills", sa.JSON(), nullable=False),
        sa.Column("recommended_actions", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_postings_user_id"), "job_postings", ["user_id"])
    op.create_table(
        "calendar_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_calendar_events_user_id"), "calendar_events", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_calendar_events_user_id"), table_name="calendar_events")
    op.drop_table("calendar_events")
    op.drop_index(op.f("ix_job_postings_user_id"), table_name="job_postings")
    op.drop_table("job_postings")
    op.drop_index(op.f("ix_weekly_reviews_user_id"), table_name="weekly_reviews")
    op.drop_table("weekly_reviews")
    op.drop_index(op.f("ix_daily_checkins_user_id"), table_name="daily_checkins")
    op.drop_index(op.f("ix_daily_checkins_date"), table_name="daily_checkins")
    op.drop_table("daily_checkins")
    op.drop_index(op.f("ix_tasks_weekly_plan_id"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_weekly_plans_user_id"), table_name="weekly_plans")
    op.drop_table("weekly_plans")
    op.drop_index(op.f("ix_roadmap_items_roadmap_id"), table_name="roadmap_items")
    op.drop_table("roadmap_items")
    op.drop_index(op.f("ix_roadmaps_user_id"), table_name="roadmaps")
    op.drop_table("roadmaps")
    op.drop_index(op.f("ix_track_competency_scores_user_id"), table_name="track_competency_scores")
    op.drop_index(op.f("ix_track_competency_scores_track_id"), table_name="track_competency_scores")
    op.drop_index(op.f("ix_track_competency_scores_axis_id"), table_name="track_competency_scores")
    op.drop_table("track_competency_scores")
    op.drop_index(op.f("ix_onboarding_profiles_user_id"), table_name="onboarding_profiles")
    op.drop_table("onboarding_profiles")
    op.drop_table("competency_axes")
    op.drop_index(op.f("ix_career_tracks_user_id"), table_name="career_tracks")
    op.drop_table("career_tracks")
    op.drop_index(op.f("ix_ai_plans_user_id"), table_name="ai_plans")
    op.drop_table("ai_plans")
    op.drop_table("users")
