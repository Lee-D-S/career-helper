from pydantic import BaseModel, Field


class UserProfileInput(BaseModel):
    name: str = "default"
    school: str | None = None
    major: str | None = None
    current_semester: str | None = None
    expected_graduation_date: str | None = None
    overall_gpa: float | None = None
    major_gpa: float | None = None
    total_credits: int | None = None


class OnboardingInput(BaseModel):
    user: UserProfileInput = Field(default_factory=UserProfileInput)
    target_roles: list[str] = Field(default_factory=list)
    target_application_start_date: str | None = None
    desired_employment_date: str | None = None
    weekday_available_hours: float | None = None
    weekend_available_hours: float | None = None
    primary_language: str | None = None
    secondary_languages: list[str] = Field(default_factory=list)
    backend_experience: str | None = None
    db_experience: str | None = None
    infra_experience: str | None = None
    frontend_experience: str | None = None
    ai_data_experience: str | None = None
    coding_test_level: str | None = None
    certificates: list[str] = Field(default_factory=list)
    language_scores: list[str] = Field(default_factory=list)
    preferred_industries: list[str] = Field(default_factory=list)
    avoided_roles: list[str] = Field(default_factory=list)
    constraints: str | None = None
    raw_notes: str | None = None


class OnboardingResponse(BaseModel):
    user_id: int
    track_count: int
    axis_count: int
