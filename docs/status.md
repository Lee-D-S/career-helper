# 개발 진행 상태

## 1. 전체 개발 프로세스

```text
Phase 0: 기획/설계
Phase 1: 프로젝트 골격
Phase 2: 온보딩/진단/트랙
Phase 3: 로드맵/주간 계획
Phase 4: 일일 체크인/주간 회고
Phase 5: AI 코칭
Phase 6: 공고/캘린더
Phase 7: 포트폴리오 정리/배포 준비
```

## 2. 현재 상태 요약

현재는 **Phase 1 완료, Phase 2 주요 흐름 구현 완료, Phase 3 초입 구현 완료, Phase 4 초입 구현 완료, Phase 5 초입 구현 완료, Phase 6 초입 구현 완료** 상태다.

```text
완료:
- 기획 문서 작성
- 데이터 모델 초안 작성
- 화면 구성 초안 작성
- 전체 실행 플랜 작성
- FastAPI 백엔드 골격
- SQLAlchemy 모델 골격
- Alembic 초기 마이그레이션
- Next.js 프론트엔드 골격
- 온보딩 입력 화면
- 대시보드 첫 화면
- Docker Compose 초안
- 온보딩 저장 후 대시보드 이동
- 초기 역량 점수 추정
- 역량 점수 수정 API
- 역량 점수 수정 화면
- 로드맵 생성/조회 API
- 로드맵 화면
- 주간 계획 생성/조회 API
- 작업 상태 수정 API
- 주간 계획 화면
- 일일 체크인 생성/조회 API
- 일일 체크인 화면
- 주간 회고 생성/조회 API
- 주간 회고 화면
- 작업 완료율 기반 주간 실행률 계산
- AIProvider 인터페이스
- MockProvider
- AI 제안 생성 API
- AI 제안 목록/상태 변경 API
- AI 제안 화면
- accepted AI 로드맵 제안을 실제 Roadmap/RoadmapItem으로 반영
- accepted AI 주간 계획 제안을 실제 WeeklyPlan/Task로 반영
- 공고 저장/조회 API
- MockProvider 기반 공고 분석 API
- 공고 저장/분석 화면

진행 중:
- 온보딩/진단/트랙/로드맵/주간 계획/체크인/회고/AI 제안/공고 흐름의 실제 DB 연동 검증

아직 미구현:
- Gemini Provider
- 내부 캘린더
- .ics 내보내기
```

## 3. Phase별 상세 상태

### Phase 0: 기획/설계

상태: 완료

산출물:

```text
docs/prd.md
docs/data-model.md
docs/screens.md
docs/plan.md
```

결정된 내용:

```text
제품명: 취업준비 도우미
형태: 개인용 웹 대시보드, 추후 다중 사용자 확장
핵심 루프: 온보딩 -> 진단 -> 로드맵 -> 주간 계획 -> 일일 체크인 -> 주간 회고
Frontend: Next.js + TypeScript + Tailwind CSS + shadcn/ui 스타일
Backend: Python + FastAPI
DB: PostgreSQL
ORM/Migration: SQLAlchemy + Alembic
AI: Gemini 무료 티어 + MockProvider, 추후 유료 Provider 확장
배포: 로컬 우선 + Docker Compose, 추후 AWS EC2 또는 Lightsail
```

### Phase 1: 프로젝트 골격

상태: 완료

구현된 파일/구조:

```text
backend/
frontend/
docs/
docker-compose.yml
.env.example
README.md
```

검증 완료:

```text
rtk python -m compileall backend\app backend\alembic
rtk python -c "import app.main"
rtk npm run build
rtk docker compose config --quiet
```

주의:

```text
Docker Desktop이 실행 중이 아니어서 전체 docker compose up 검증은 아직 미완료.
프론트엔드 개발 서버는 로컬에서 실행 가능.
```

### Phase 2: 온보딩/진단/트랙

상태: 주요 흐름 구현, 실제 DB 연동 검증 필요

구현됨:

```text
POST /api/onboarding
GET /api/dashboard
PATCH /api/scores/{score_id}
OnboardingProfile 모델
User 모델
CareerTrack 모델
CompetencyAxis 모델
TrackCompetencyScore 모델
온보딩 화면
대시보드 요약 화면
역량 점수 수정 화면
온보딩 기반 초기 점수 추정
```

현재 동작 목표:

```text
사용자가 온보딩 정보를 입력한다.
기본 직무 트랙을 생성한다.
10개 역량 축을 생성한다.
트랙별 초기 점수를 생성한다.
대시보드에서 목표 트랙과 부족 역량 Top 3를 표시한다.
사용자가 역량별 현재 점수, 목표 점수, 증거 메모를 수정한다.
```

남은 작업:

```text
트랙 우선순위 수정
초기 점수 추정 로직 고도화
실제 PostgreSQL 환경에서 온보딩 저장 검증
실제 PostgreSQL 환경에서 점수 수정 검증
```

### Phase 3: 로드맵/주간 계획

상태: 일부 구현

구현됨:

```text
GET /api/roadmaps
POST /api/roadmaps
GET /api/weekly-plans
POST /api/weekly-plans
PATCH /api/tasks/{task_id}
로드맵 생성/조회 화면
주간 계획 생성/조회 화면
작업 todo/done 상태 변경
이번 주 계획 대시보드 연결
```

남은 작업:

```text
로드맵 수정/삭제
로드맵 항목 상태 변경
주간 계획 수정/삭제
작업 상세 수정
계획 승인/수정/거절 상태
AI 제안 계획과 수동 계획 구분
```

### Phase 4: 일일 체크인/주간 회고

상태: 일부 구현

구현됨:

```text
GET /api/daily-checkins
POST /api/daily-checkins
GET /api/weekly-reviews
POST /api/weekly-reviews
일일 체크인 생성/조회 화면
주간 회고 생성/조회 화면
계획 대비 실행률 계산
미완료 원인 기록
다음 주 우선순위 조정 근거 저장
최근 체크인 대시보드 연결
```

남은 작업:

```text
체크인 수정/삭제
회고 수정/삭제
회고에서 다음 주 계획 자동 생성
일일 체크인 기반 주간 실제 투입 시간 집계
```

### Phase 5: AI 코칭

상태: 일부 구현

구현됨:

```text
AIProvider 인터페이스
MockProvider
GET /api/ai-plans
POST /api/ai-suggestions
PATCH /api/ai-plans/{plan_id}
로드맵/주간 계획/주간 회고/공고 분석 Mock 제안 생성
AI 제안 승인/거절 상태 변경
AI 제안 화면
승인한 로드맵 제안 실제 로드맵 반영
승인한 주간 계획 제안 실제 주간 계획 반영
```

남은 작업:

```text
GeminiProvider
구조화 JSON 응답 검증
AI 실패 시 수동 fallback
사용자 수정 상태 edited 처리
공고 본문 기반 분석 입력
주간 회고 제안 실제 회고 초안 반영
```

### Phase 6: 공고/캘린더

상태: 일부 구현

구현됨:

```text
GET /api/job-postings
POST /api/job-postings
POST /api/job-postings/{job_id}/analyze
공고 URL/본문 저장
MockProvider 기반 공고 요약/분류
공고 저장/분석 화면
```

남은 작업:

```text
공고 수정/삭제
공고 상태 변경
실제 Gemini 기반 공고 분석
CalendarEvent CRUD
내부 캘린더 화면
.ics 내보내기
```

### Phase 7: 포트폴리오 정리/배포 준비

상태: 미구현

예정 작업:

```text
Docker Compose 전체 실행 검증
README 보강
스크린샷 추가
배포 문서 작성
AWS EC2 또는 Lightsail 배포 검토
```

## 4. 다음 추천 작업

가장 가까운 다음 작업은 실제 DB 연동 검증 후 Phase 5 AI 코칭 기반을 시작하는 것이다.

우선순위:

```text
1. Docker Desktop 실행 후 docker compose up 검증
2. 온보딩 저장 실제 동작 확인
3. 역량 점수 수정 실제 동작 확인
4. 로드맵/주간 계획 생성 실제 동작 확인
5. 일일 체크인/주간 회고 실제 동작 확인
6. AI 제안 생성/승인/거절/실제 데이터 반영 확인
7. 공고 저장/분석 실제 동작 확인
8. 내부 캘린더 구현
```

## 5. 갱신 규칙

구현이 진행될 때마다 이 문서를 갱신한다.

갱신 기준:

```text
새 API 추가
새 화면 추가
DB 모델 또는 마이그레이션 변경
Phase 상태 변경
검증 명령 추가
실행/배포 방식 변경
```
