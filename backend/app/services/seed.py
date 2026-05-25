from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career import CompetencyAxis

AXES = [
    "프로그래밍 언어",
    "백엔드/API",
    "DB/SQL",
    "인프라/배포",
    "코딩테스트",
    "포트폴리오/프로젝트",
    "도메인 지식",
    "서류/면접",
    "업무 관련 자격증",
    "어학성적",
]

FINANCE_IT_WEIGHTS = {
    "프로그래밍 언어": 0.12,
    "백엔드/API": 0.14,
    "DB/SQL": 0.12,
    "인프라/배포": 0.10,
    "코딩테스트": 0.12,
    "포트폴리오/프로젝트": 0.16,
    "도메인 지식": 0.10,
    "서류/면접": 0.08,
    "업무 관련 자격증": 0.04,
    "어학성적": 0.02,
}


async def ensure_competency_axes(db: AsyncSession) -> list[CompetencyAxis]:
    result = await db.execute(select(CompetencyAxis))
    existing = {axis.name: axis for axis in result.scalars()}

    for name in AXES:
        if name not in existing:
            axis = CompetencyAxis(name=name, description=None)
            db.add(axis)
            existing[name] = axis

    await db.flush()
    return [existing[name] for name in AXES]
