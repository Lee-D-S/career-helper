from typing import Any, Protocol


class AIProvider(Protocol):
    async def generate_roadmap(self) -> dict[str, Any]:
        ...

    async def generate_weekly_plan(self) -> dict[str, Any]:
        ...

    async def generate_weekly_review(self) -> dict[str, Any]:
        ...

    async def analyze_job_posting(self, content: str | None = None) -> dict[str, Any]:
        ...


class MockProvider:
    async def generate_roadmap(self) -> dict[str, Any]:
        return {
            "monthly_goal": "auto-invest 포트폴리오화와 SQL/코딩테스트 기초 복구에 집중한다.",
            "items": [
                {
                    "title": "auto-invest README 1차 작성",
                    "reason": "금융 IT 포트폴리오 증거를 빠르게 강화할 수 있음",
                    "priority": 1,
                },
                {
                    "title": "핵심 API와 DB 구조 정리",
                    "reason": "백엔드/API와 DB 역량을 면접에서 설명 가능한 상태로 만들기 위함",
                    "priority": 2,
                },
                {
                    "title": "SQL 기본 SELECT/JOIN/GROUP BY 복습",
                    "reason": "금융 IT 직무에서 DB/SQL 약점을 보완하기 위함",
                    "priority": 3,
                },
            ],
        }

    async def generate_weekly_plan(self) -> dict[str, Any]:
        return {
            "weekly_goal": "포트폴리오 증거와 기초 역량을 동시에 보강한다.",
            "tasks": [
                {
                    "title": "auto-invest README 초안 작성",
                    "category": "portfolio",
                    "estimated_hours": 4,
                    "reason": "채용 담당자가 프로젝트 목적과 구조를 빠르게 이해하게 하기 위함",
                },
                {
                    "title": "SQL JOIN/GROUP BY 20문제 풀이",
                    "category": "sql",
                    "estimated_hours": 5,
                    "reason": "DB/SQL 기본기를 직접 작성 가능한 수준으로 올리기 위함",
                },
                {
                    "title": "프로그래머스 Lv2 3문제 풀이",
                    "category": "coding_test",
                    "estimated_hours": 4,
                    "reason": "9월 지원 전 코딩테스트 최소 기준을 맞추기 위함",
                },
            ],
        }

    async def generate_weekly_review(self) -> dict[str, Any]:
        return {
            "summary": "완료한 작업과 막힌 점을 기준으로 다음 주 계획을 줄이고 우선순위를 재정렬한다.",
            "review_questions": [
                "계획 대비 실제 투입 시간이 충분했는가?",
                "미완료 원인은 시간 부족, 난이도, 우선순위 오류 중 무엇인가?",
                "다음 주에도 유지할 작업과 삭제할 작업은 무엇인가?",
            ],
        }

    async def analyze_job_posting(self, content: str | None = None) -> dict[str, Any]:
        text = (content or "").lower()
        required_skills = ["SQL", "API 연동", "금융 도메인 이해"]
        if "spring" in text or "java" in text:
            required_skills.insert(0, "Java/Spring")
        if "python" in text or "fastapi" in text:
            required_skills.insert(0, "Python/FastAPI")
        if "aws" in text or "docker" in text:
            required_skills.append("AWS/Docker")

        return {
            "summary": "금융 IT/백엔드 역량과 연결되는 공고로 보고, 프로젝트 설명과 SQL/API 역량 보완이 필요합니다.",
            "fit_score": 65,
            "required_skills": required_skills,
            "recommended_actions": [
                "auto-invest의 API, DB, 리스크 관리 구조를 공고 요구 역량에 맞춰 요약",
                "SQL 직접 작성 경험을 보완할 문제 풀이 기록 추가",
                "인턴 경험을 거래 시스템/SaaS 운영 경험 중심으로 재정리",
            ],
        }


def get_ai_provider() -> AIProvider:
    return MockProvider()
