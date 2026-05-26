import asyncio
import json
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class AIProviderError(RuntimeError):
    pass


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


class GeminiProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def generate_roadmap(self) -> dict[str, Any]:
        return await self._generate_json(
            """
사용자의 취업 준비를 돕기 위한 1개월 로드맵을 생성해줘.
금융 IT 풀스택, 백엔드/API, DB/SQL, 포트폴리오 강화 관점으로 작성해.
각 항목은 바로 실행 가능한 산출물 중심이어야 해.
""",
            {
                "type": "OBJECT",
                "properties": {
                    "monthly_goal": {"type": "STRING"},
                    "items": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "title": {"type": "STRING"},
                                "reason": {"type": "STRING"},
                                "priority": {"type": "INTEGER"},
                            },
                            "required": ["title", "reason", "priority"],
                        },
                    },
                },
                "required": ["monthly_goal", "items"],
            },
            required_keys=["monthly_goal", "items"],
        )

    async def generate_weekly_plan(self) -> dict[str, Any]:
        return await self._generate_json(
            """
이번 주 취업 준비 실행 계획을 생성해줘.
포트폴리오, SQL, 코딩테스트, 서류/면접 중 우선순위를 골라 과하게 많지 않은 작업으로 작성해.
각 작업은 예상 시간을 포함해야 해.
""",
            {
                "type": "OBJECT",
                "properties": {
                    "weekly_goal": {"type": "STRING"},
                    "tasks": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "title": {"type": "STRING"},
                                "category": {"type": "STRING"},
                                "estimated_hours": {"type": "NUMBER"},
                                "reason": {"type": "STRING"},
                            },
                            "required": ["title", "category", "estimated_hours", "reason"],
                        },
                    },
                },
                "required": ["weekly_goal", "tasks"],
            },
            required_keys=["weekly_goal", "tasks"],
        )

    async def generate_weekly_review(self) -> dict[str, Any]:
        return await self._generate_json(
            """
취업 준비 주간 회고 초안을 생성해줘.
계획 대비 실행률, 미완료 원인, 다음 주 조정 기준을 점검할 수 있게 작성해.
""",
            {
                "type": "OBJECT",
                "properties": {
                    "summary": {"type": "STRING"},
                    "review_questions": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
                "required": ["summary", "review_questions"],
            },
            required_keys=["summary", "review_questions"],
        )

    async def analyze_job_posting(self, content: str | None = None) -> dict[str, Any]:
        posting = content or "공고 본문이 제공되지 않았습니다."
        return await self._generate_json(
            f"""
다음 채용 공고를 취업 준비 관점에서 분석해줘.
지원자는 금융 IT 풀스택/백엔드 직무를 준비하고 있고, Python/FastAPI, SQL, 포트폴리오 프로젝트를 강화 중이야.

공고:
{posting}
""",
            {
                "type": "OBJECT",
                "properties": {
                    "summary": {"type": "STRING"},
                    "fit_score": {"type": "NUMBER"},
                    "required_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "recommended_actions": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
                "required": ["summary", "fit_score", "required_skills", "recommended_actions"],
            },
            required_keys=["summary", "fit_score", "required_skills", "recommended_actions"],
        )

    async def _generate_json(
        self,
        prompt: str,
        response_schema: dict[str, Any],
        required_keys: list[str],
    ) -> dict[str, Any]:
        raw = await asyncio.to_thread(self._request, prompt.strip(), response_schema)
        text = self._extract_text(raw)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise AIProviderError("Gemini returned invalid JSON") from exc
        if not isinstance(parsed, dict):
            raise AIProviderError("Gemini returned a non-object JSON response")
        missing = [key for key in required_keys if key not in parsed]
        if missing:
            raise AIProviderError(f"Gemini response missing keys: {', '.join(missing)}")
        return parsed

    def _request(self, prompt: str, response_schema: dict[str, Any]) -> dict[str, Any]:
        body = {
            "system_instruction": {
                "parts": {
                    "text": (
                        "너는 한국어 취업 준비 코치다. 반드시 요청한 JSON schema에 맞는 JSON만 반환한다. "
                        "마크다운 코드블록이나 설명 문장은 쓰지 않는다."
                    )
                }
            },
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            },
        }
        request = Request(
            GEMINI_API_URL.format(model=self.model),
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "x-goog-api-key": self.api_key,
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise AIProviderError(f"Gemini API request failed: HTTP {exc.code} {detail}") from exc
        except (URLError, TimeoutError) as exc:
            raise AIProviderError(f"Gemini API request failed: {exc}") from exc

    def _extract_text(self, payload: dict[str, Any]) -> str:
        try:
            parts = payload["candidates"][0]["content"]["parts"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("Gemini response did not include candidate text") from exc
        texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
        text = "".join(texts).strip()
        if not text:
            raise AIProviderError("Gemini response text was empty")
        return text


def get_ai_provider() -> AIProvider:
    settings = get_settings()
    if settings.ai_provider.lower() == "gemini":
        if not settings.gemini_api_key:
            raise AIProviderError("GEMINI_API_KEY is required when AI_PROVIDER=gemini")
        return GeminiProvider(settings.gemini_api_key, settings.gemini_model)
    return MockProvider()
