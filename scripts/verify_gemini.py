from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.ai_provider import AIProviderError, GeminiProvider  # noqa: E402


def load_root_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


async def main() -> None:
    load_root_env()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is empty. Add it to .env before running this check.")

    provider = GeminiProvider(api_key=api_key, model=model)
    try:
        result = await provider.analyze_job_posting(
            "Python, FastAPI, SQL, Docker 경험을 요구하는 금융 IT 백엔드 인턴 공고"
        )
    except AIProviderError as exc:
        raise SystemExit(f"Gemini verification failed: {exc}") from exc

    required = {"summary", "fit_score", "required_skills", "recommended_actions"}
    missing = sorted(required - set(result))
    if missing:
        raise SystemExit(f"Gemini verification failed: missing keys {', '.join(missing)}")

    print("Gemini verification ok")
    print(f"model={model}")
    print(f"fit_score={result['fit_score']}")
    print(f"required_skills={len(result['required_skills'])}")
    print(f"recommended_actions={len(result['recommended_actions'])}")


if __name__ == "__main__":
    asyncio.run(main())
