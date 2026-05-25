# 전체 실행 플랜

## 1. 현재 전략

취업준비 도우미는 개인용 취업 코칭 웹 대시보드로 시작한다.

서비스의 목적은 취업 준비 항목을 나열하는 것이 아니라, 목표 직무와 현재 상태를 비교해 합격 가능성을 높이는 실행 계획을 지속적으로 조정하는 것이다.

## 2. 사용자 현재 상태 요약

```text
현재 학기: 4-1, 인턴 중
졸업 예정: 2027년 2월
본격 지원 시작: 2026년 9월
하루 평균 공부 가능 시간: 3~4시간
주말 공부 가능 시간: 5~6시간
```

기술 상태:

```text
주 언어: Python 1순위, TypeScript/JavaScript 2순위, Java 3순위
언어 숙련도: 전반적으로 낮음
백엔드 프레임워크: 경험 없음
DB: PostgreSQL 사용 경험 있음, SQL 직접 작성 역량은 약함
인프라/배포: AWS/Linux 기초, Docker 경험 없음
코딩테스트: 프로그래머스 Lv1~2
도메인: 거래 시스템/SaaS 관련 인턴 경험 있음
```

학벌과 학점은 준비도 평가 축이 아니라 기본 프로필로 관리한다. AI는 이를 서류 리스크 분석과 보완 전략 생성에 사용한다.

## 3. 포트폴리오 전략

핵심 포트폴리오는 `auto-invest`다.

대표 메시지는 다음과 같다.

```text
개인 투자자의 감정적 의사결정을 줄이기 위해,
시장 데이터 수집부터 전략 평가, 리스크 검토, 주문 실행,
운영 리포트까지 자동화한 금융 의사결정 지원 시스템
```

`auto-invest` 강화 방향:

```text
Python/FastAPI 프로젝트를 완성도 있게 포트폴리오화
README
아키텍처 다이어그램
API 문서
DB ERD
Docker 실행
핵심 API 테스트
투자 파이프라인 설명
대시보드 화면 또는 Swagger 캡처
```

문서화 우선순위:

```text
1. README.md 1차 작성
2. 아키텍처 다이어그램
3. 핵심 API 목록/Swagger 캡처
4. DB ERD
5. 핵심 파이프라인 설명
6. 테스트/실행 방법
7. 포트폴리오용 요약본
```

## 4. 취업 준비 로드맵

### 2026년 5월 말~6월: 기반 정리

목표:

```text
auto-invest 포트폴리오화
인턴 경험 정리
SQL/코딩테스트 기초 복구
```

주요 산출물:

```text
auto-invest README 1차
아키텍처 다이어그램 초안
핵심 API 목록
인턴 경험 이력서 bullet
SQL 기본 문제 풀이 기록
프로그래머스 Lv2 풀이 기록
```

### 2026년 7월: 취업 자료 제작

목표:

```text
이력서, 포트폴리오, GitHub 정리
금융 IT 직무 기준 자기소개서 템플릿 작성
```

주요 산출물:

```text
1페이지 이력서
포트폴리오 PDF 또는 웹 페이지
GitHub pinned repository 정리
공통 자기소개서 소재
auto-invest 기술 설명 문서
```

### 2026년 8월: 실전 지원 준비

목표:

```text
공고 분석
기업별 맞춤 서류
모의면접
코딩테스트 Lv2 안정화
```

주요 산출물:

```text
지원 기업 리스트
공고별 요구 역량 분석
기업별 지원 전략
기술 면접 예상 질문
프로젝트 설명 스크립트
```

### 2026년 9월~2027년 2월: 지원/개선 루프

목표:

```text
지속 지원
탈락 원인 분석
면접 복기
부족 역량 보완
```

주요 산출물:

```text
지원 현황 트래커
면접 복기
서류/코테/면접 전환율
다음 주 개선 계획
```

## 5. MVP 구현 단계

### Phase 1: 프로젝트 골격

```text
Next.js 앱 생성
Tailwind CSS 설정
shadcn/ui 설정
FastAPI 앱 생성
PostgreSQL 연결
SQLAlchemy 설정
Alembic 마이그레이션 설정
Docker Compose 초안 작성
기본 user_id=1 구조
개발 실행 문서 작성
```

검증:

```text
프론트엔드 로컬 실행
백엔드 /health 응답
DB 연결 확인
초기 마이그레이션 실행
Docker Compose로 frontend/backend/db 실행 확인
```

### Phase 2: 진단 및 트랙

```text
초기 온보딩 입력 화면
OnboardingProfile 저장
목표 직무 트랙 CRUD
10개 역량 축 seed
트랙별 점수 입력/수정
대시보드 준비도 요약
```

검증:

```text
금융 IT 풀스택 트랙 생성
온보딩 입력으로 초기 점수 제안
10개 축 점수 저장
부족 역량 Top 3 계산
```

### Phase 3: 로드맵과 주간 계획

```text
월간 로드맵 관리
주간 계획 관리
작업 상태 관리
AI 제안 상태 모델링
```

검증:

```text
6월 로드맵 생성
이번 주 계획 생성
작업 완료 처리
```

### Phase 4: 일일 체크인과 주간 회고

```text
일일 체크인 입력
주간 실행률 계산
주간 회고 생성
다음 주 조정 근거 저장
```

검증:

```text
일일 체크인 3개 이상 저장
주간 회고 생성
계획 대비 실행률 계산
```

### Phase 5: AI 코칭

```text
AIProvider 인터페이스 작성
MockProvider 작성
Gemini 무료 티어 Provider 작성
AI 입력 데이터 구성
구조화 JSON 응답 파싱
사용자용 설명문 저장
제안 승인/수정/거절 흐름
AI 실패 시 수동 작성 fallback
```

검증:

```text
MockProvider로 로드맵/주간 계획 제안 생성
GeminiProvider로 샘플 제안 생성
로드맵 제안 생성
주간 계획 제안 생성
accepted 상태 계획 반영
AI 없이 수동 계획 작성 가능
```

### Phase 6: 공고와 캘린더

```text
공고 URL/본문 저장
AI 요약/분류
내부 캘린더
.ics 내보내기
```

검증:

```text
공고 1개 저장
마감일 캘린더 표시
.ics 파일 생성
```

## 6. 추후 확장

```text
인증/로그인
자동 공고 크롤링
Google Calendar 연동
이력서 자동 생성
자기소개서 첨삭
면접 음성 연습
자격증 강의 추천
커뮤니티
다중 사용자 SaaS 전환
```

## 7. 확정된 기술/운영 선택

현재 확정된 선택은 다음과 같다.

```text
AI: Gemini 무료 티어 + MockProvider, 추후 유료 Provider 확장
Backend ORM: SQLAlchemy + Alembic
Frontend UI: Tailwind CSS + shadcn/ui
Deployment: 로컬 우선 + Docker Compose 준비, 추후 AWS EC2 또는 Lightsail
auto-invest 문서화 우선순위: README -> 아키텍처 -> API -> ERD -> 파이프라인 -> 테스트/실행 -> 요약본
```
