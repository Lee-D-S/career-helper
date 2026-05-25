# 취업준비 도우미

개인화 취업 준비 코칭 웹 대시보드입니다. 초기 MVP는 개인용으로 동작하며, 추후 다중 사용자 서비스로 확장할 수 있게 `user_id` 기반 데이터 구조를 사용합니다.

## 구조

```text
backend/   Python + FastAPI + SQLAlchemy + Alembic
frontend/  Next.js + TypeScript + Tailwind CSS + shadcn/ui 스타일
docs/      PRD, 데이터 모델, 화면 구성, 전체 플랜
```

개발 진행 상태는 [docs/status.md](docs/status.md)에서 추적합니다.

## 로컬 실행

### Backend

```bash
cd backend
rtk python -m venv .venv
.venv\Scripts\activate
rtk python -m pip install -r requirements.txt
copy .env.example .env
rtk alembic upgrade head
rtk uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
rtk npm install
rtk npm run dev
```

## Docker Compose

```bash
copy .env.example .env
rtk docker compose up --build
```

## MVP 첫 흐름

1. `/onboarding`에서 사전 정보를 입력한다.
2. 백엔드가 기본 직무 트랙과 10개 역량 축을 생성한다.
3. `/` 대시보드에서 목표 트랙, 준비도, 부족 역량 Top 3를 확인한다.
