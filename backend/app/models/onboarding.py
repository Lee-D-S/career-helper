from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OnboardingProfile(Base):
    __tablename__ = "onboarding_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    target_roles: Mapped[list[str]] = mapped_column(JSON, default=list)
    target_application_start_date: Mapped[str | None] = mapped_column(Text)
    desired_employment_date: Mapped[str | None] = mapped_column(Text)
    weekday_available_hours: Mapped[float | None] = mapped_column(Float)
    weekend_available_hours: Mapped[float | None] = mapped_column(Float)
    primary_language: Mapped[str | None] = mapped_column(Text)
    secondary_languages: Mapped[list[str]] = mapped_column(JSON, default=list)
    backend_experience: Mapped[str | None] = mapped_column(Text)
    db_experience: Mapped[str | None] = mapped_column(Text)
    infra_experience: Mapped[str | None] = mapped_column(Text)
    frontend_experience: Mapped[str | None] = mapped_column(Text)
    ai_data_experience: Mapped[str | None] = mapped_column(Text)
    coding_test_level: Mapped[str | None] = mapped_column(Text)
    certificates: Mapped[list[str]] = mapped_column(JSON, default=list)
    language_scores: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_industries: Mapped[list[str]] = mapped_column(JSON, default=list)
    avoided_roles: Mapped[list[str]] = mapped_column(JSON, default=list)
    constraints: Mapped[str | None] = mapped_column(Text)
    raw_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
