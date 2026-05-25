from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CareerTrack(Base):
    __tablename__ = "career_tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    priority: Mapped[int] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    target_start_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CompetencyAxis(Base):
    __tablename__ = "competency_axes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str | None] = mapped_column(Text)


class TrackCompetencyScore(Base):
    __tablename__ = "track_competency_scores"
    __table_args__ = (UniqueConstraint("track_id", "axis_id", name="uq_track_axis"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("career_tracks.id"), index=True)
    axis_id: Mapped[int] = mapped_column(ForeignKey("competency_axes.id"), index=True)
    score: Mapped[float] = mapped_column(Float, default=0)
    evidence: Mapped[str | None] = mapped_column(Text)
    target_score: Mapped[float] = mapped_column(Float, default=3)
    weight: Mapped[float] = mapped_column(Float, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
