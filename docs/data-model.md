# 데이터 모델 초안

## 1. 설계 원칙

- MVP는 단일 사용자 모드로 동작한다.
- 추후 인증 추가를 고려해 주요 엔티티에는 `user_id`를 둔다.
- AI가 제안한 데이터와 사용자가 승인한 데이터를 구분한다.
- 할 일보다 목표 직무 트랙과 역량 진단을 중심 모델로 둔다.

## 2. 주요 엔티티

### User

MVP에서는 실제 로그인 없이 기본 사용자 1명만 사용한다.

```text
id
name
school
major
current_semester
expected_graduation_date
overall_gpa
major_gpa
total_credits
created_at
updated_at
```

학벌과 학점은 준비도 평가 축이 아니라 사용자 기본 프로필로 관리한다. AI는 이를 서류 리스크 분석과 보완 전략 생성에 사용한다.

### CareerTrack

목표 직무 트랙이다.

```text
id
user_id
name
priority
description
target_start_date
created_at
updated_at
```

초기 트랙:

```text
금융 IT 풀스택
백엔드/서버
AI
데이터
```

### CompetencyAxis

역량 평가 축이다.

```text
id
name
description
```

초기 축:

```text
프로그래밍 언어
백엔드/API
DB/SQL
인프라/배포
코딩테스트
포트폴리오/프로젝트
도메인 지식
서류/면접
업무 관련 자격증
어학성적
```

### TrackCompetencyScore

직무 트랙별 역량 점수다.

```text
id
user_id
track_id
axis_id
score
evidence
target_score
weight
updated_at
```

`score`와 `target_score`는 0~5 범위를 사용한다.

### OnboardingProfile

초기 온보딩/진단에서 수집한 사용자 사전 정보다.

```text
id
user_id
target_roles
target_application_start_date
desired_employment_date
weekday_available_hours
weekend_available_hours
primary_language
secondary_languages
backend_experience
db_experience
infra_experience
frontend_experience
ai_data_experience
coding_test_level
certificates
language_scores
preferred_industries
avoided_roles
constraints
raw_notes
created_at
updated_at
```

온보딩 데이터는 첫 직무 트랙, 역량 점수, 로드맵 생성을 위한 입력으로 사용한다.

### Artifact

포트폴리오, 인턴 경험, 공모전 경험, 자격증 등 증명 가능한 산출물이다.

```text
id
user_id
title
type
description
url
status
started_at
completed_at
created_at
updated_at
```

예:

```text
auto-invest
네티모 인턴
블록웨이브랩스 인턴
공모전 참여 경험
SQLD
OPIc
```

### Roadmap

전체 로드맵이다.

```text
id
user_id
track_id
title
start_date
end_date
status
ai_plan_id
created_at
updated_at
```

### RoadmapItem

로드맵의 월간 또는 단계별 목표다.

```text
id
roadmap_id
title
description
start_date
end_date
priority
status
```

### WeeklyPlan

이번 주 실행 계획이다.

```text
id
user_id
track_id
week_start
week_end
title
status
ai_plan_id
created_at
updated_at
```

### Task

주간 계획에 속한 실행 항목이다.

```text
id
weekly_plan_id
title
category
description
estimated_hours
actual_hours
status
due_date
reason
created_at
updated_at
```

카테고리 예:

```text
portfolio
backend
sql
coding_test
resume
interview
certificate
language
job_posting
```

### DailyCheckIn

일일 체크인이다.

```text
id
user_id
date
actual_hours
completed_work
blockers
created_at
updated_at
```

### WeeklyReview

주간 회고다.

```text
id
user_id
weekly_plan_id
completion_rate
blockers
priority_adjustments
score_changes
summary
created_at
updated_at
```

회고 판단 기준:

```text
1. 이번 주 계획을 얼마나 완료했는가?
2. 완료하지 못한 이유는 시간 부족, 난이도, 우선순위 오류 중 무엇인가?
3. 다음 주 계획에서 무엇을 유지/삭제/조정할 것인가?
4. 준비도 점수가 실제로 올라갔는가?
```

### JobPosting

사용자가 URL 또는 본문으로 저장한 공고다.

```text
id
user_id
company_name
position_title
source_url
raw_content
deadline
status
fit_score
summary
required_skills
recommended_actions
created_at
updated_at
```

공고 상태 예:

```text
saved
analyzing
ready
applied
rejected
interviewing
offer
archived
```

### CalendarEvent

내부 캘린더 일정이다.

```text
id
user_id
title
description
start_at
end_at
event_type
source_type
source_id
created_at
updated_at
```

이벤트 타입 예:

```text
task
job_deadline
certificate_exam
language_test
review
```

### AiPlan

AI가 생성한 계획 또는 분석 결과다.

```text
id
user_id
plan_type
raw_response
parsed_json
user_explanation
validation_status
decision_status
created_at
updated_at
```

`decision_status`:

```text
suggested
accepted
edited
rejected
```

## 3. 주요 관계

```text
User 1 - N CareerTrack
User 1 - 1 OnboardingProfile
CareerTrack 1 - N TrackCompetencyScore
CompetencyAxis 1 - N TrackCompetencyScore
CareerTrack 1 - N Roadmap
Roadmap 1 - N RoadmapItem
CareerTrack 1 - N WeeklyPlan
WeeklyPlan 1 - N Task
WeeklyPlan 1 - 1 WeeklyReview
User 1 - N DailyCheckIn
User 1 - N JobPosting
User 1 - N CalendarEvent
User 1 - N AiPlan
AiPlan 1 - N Roadmap
AiPlan 1 - N WeeklyPlan
```
