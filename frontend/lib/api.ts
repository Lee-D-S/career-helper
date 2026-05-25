const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export type AxisScore = {
  id: number;
  track_id: number;
  axis_id: number;
  axis: string;
  score: number;
  target_score: number;
  weight: number;
  evidence?: string | null;
};

export type TrackReadiness = {
  id: number;
  name: string;
  priority: number;
  weighted_score: number;
  scores: AxisScore[];
};

export type DashboardSummary = {
  target_track: string | null;
  readiness: TrackReadiness[];
  weakest_axes: AxisScore[];
};

export type RoadmapItem = {
  id: number;
  roadmap_id: number;
  title: string;
  description?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  priority: number;
  status: string;
};

export type Roadmap = {
  id: number;
  title: string;
  track_id?: number | null;
  start_date?: string | null;
  end_date?: string | null;
  status: string;
  items: RoadmapItem[];
};

export type Task = {
  id: number;
  weekly_plan_id: number;
  title: string;
  category: string;
  description?: string | null;
  estimated_hours?: number | null;
  actual_hours?: number | null;
  status: string;
  due_date?: string | null;
  reason?: string | null;
};

export type WeeklyPlan = {
  id: number;
  title: string;
  track_id?: number | null;
  week_start: string;
  week_end: string;
  status: string;
  tasks: Task[];
};

export type DailyCheckIn = {
  id: number;
  date: string;
  actual_hours: number;
  completed_work: string;
  blockers?: string | null;
};

export type WeeklyReview = {
  id: number;
  weekly_plan_id: number;
  completion_rate: number;
  blockers?: string | null;
  priority_adjustments?: string | null;
  score_changes?: string | null;
  summary?: string | null;
};

export type AiPlan = {
  id: number;
  plan_type: string;
  raw_response?: string | null;
  parsed_json?: Record<string, unknown> | null;
  user_explanation?: string | null;
  validation_status: string;
  decision_status: string;
  applied_resource_type?: string | null;
  applied_resource_id?: number | null;
  created_at: string;
};

export type JobPosting = {
  id: number;
  company_name?: string | null;
  position_title?: string | null;
  source_url?: string | null;
  raw_content?: string | null;
  deadline?: string | null;
  status: string;
  fit_score?: number | null;
  summary?: string | null;
  required_skills: string[];
  recommended_actions: string[];
};

export type CalendarEvent = {
  id: number;
  title: string;
  description?: string | null;
  start_at: string;
  end_at?: string | null;
  event_type: string;
  source_type?: string | null;
  source_id?: number | null;
};

export async function getDashboard(): Promise<DashboardSummary> {
  const response = await fetch(`${API_BASE_URL}/dashboard`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("대시보드를 불러오지 못했습니다.");
  }
  return response.json();
}

export async function submitOnboarding(payload: unknown) {
  const response = await fetch(`${API_BASE_URL}/onboarding`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("온보딩 저장에 실패했습니다.");
  }

  return response.json();
}

export async function updateScore(
  scoreId: number,
  payload: { score: number; target_score?: number; evidence?: string | null }
): Promise<AxisScore> {
  const response = await fetch(`${API_BASE_URL}/scores/${scoreId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("역량 점수 저장에 실패했습니다.");
  }

  return response.json();
}

export async function getRoadmaps(): Promise<Roadmap[]> {
  const response = await fetch(`${API_BASE_URL}/roadmaps`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("로드맵을 불러오지 못했습니다.");
  }
  return response.json();
}

export async function createRoadmap(payload: unknown): Promise<Roadmap> {
  const response = await fetch(`${API_BASE_URL}/roadmaps`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("로드맵 저장에 실패했습니다.");
  }
  return response.json();
}

export async function getWeeklyPlans(): Promise<WeeklyPlan[]> {
  const response = await fetch(`${API_BASE_URL}/weekly-plans`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("주간 계획을 불러오지 못했습니다.");
  }
  return response.json();
}

export async function createWeeklyPlan(payload: unknown): Promise<WeeklyPlan> {
  const response = await fetch(`${API_BASE_URL}/weekly-plans`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("주간 계획 저장에 실패했습니다.");
  }
  return response.json();
}

export async function updateTask(taskId: number, payload: Partial<Task>): Promise<Task> {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("작업 저장에 실패했습니다.");
  }
  return response.json();
}

export async function getDailyCheckIns(): Promise<DailyCheckIn[]> {
  const response = await fetch(`${API_BASE_URL}/daily-checkins`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("일일 체크인을 불러오지 못했습니다.");
  }
  return response.json();
}

export async function createDailyCheckIn(payload: unknown): Promise<DailyCheckIn> {
  const response = await fetch(`${API_BASE_URL}/daily-checkins`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("일일 체크인 저장에 실패했습니다.");
  }
  return response.json();
}

export async function getWeeklyReviews(): Promise<WeeklyReview[]> {
  const response = await fetch(`${API_BASE_URL}/weekly-reviews`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("주간 회고를 불러오지 못했습니다.");
  }
  return response.json();
}

export async function createWeeklyReview(payload: unknown): Promise<WeeklyReview> {
  const response = await fetch(`${API_BASE_URL}/weekly-reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("주간 회고 저장에 실패했습니다.");
  }
  return response.json();
}

export async function getAiPlans(): Promise<AiPlan[]> {
  const response = await fetch(`${API_BASE_URL}/ai-plans`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("AI 제안을 불러오지 못했습니다.");
  }
  return response.json();
}

export async function createAiSuggestion(planType: string): Promise<AiPlan> {
  const response = await fetch(`${API_BASE_URL}/ai-suggestions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plan_type: planType })
  });
  if (!response.ok) {
    throw new Error("AI 제안 생성에 실패했습니다.");
  }
  return response.json();
}

export async function updateAiPlanDecision(planId: number, decisionStatus: string): Promise<AiPlan> {
  const response = await fetch(`${API_BASE_URL}/ai-plans/${planId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision_status: decisionStatus })
  });
  if (!response.ok) {
    throw new Error("AI 제안 상태 저장에 실패했습니다.");
  }
  return response.json();
}

export async function getJobPostings(): Promise<JobPosting[]> {
  const response = await fetch(`${API_BASE_URL}/job-postings`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("공고를 불러오지 못했습니다.");
  }
  return response.json();
}

export async function createJobPosting(payload: unknown): Promise<JobPosting> {
  const response = await fetch(`${API_BASE_URL}/job-postings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("공고 저장에 실패했습니다.");
  }
  return response.json();
}

export async function analyzeJobPosting(jobId: number): Promise<JobPosting> {
  const response = await fetch(`${API_BASE_URL}/job-postings/${jobId}/analyze`, {
    method: "POST"
  });
  if (!response.ok) {
    throw new Error("공고 분석에 실패했습니다.");
  }
  return response.json();
}

export async function getCalendarEvents(): Promise<CalendarEvent[]> {
  const response = await fetch(`${API_BASE_URL}/calendar-events`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("캘린더 일정을 불러오지 못했습니다.");
  }
  return response.json();
}

export async function createCalendarEvent(payload: unknown): Promise<CalendarEvent> {
  const response = await fetch(`${API_BASE_URL}/calendar-events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("캘린더 일정 저장에 실패했습니다.");
  }
  return response.json();
}

export async function syncCalendarEvents(): Promise<CalendarEvent[]> {
  const response = await fetch(`${API_BASE_URL}/calendar-events/sync`, {
    method: "POST"
  });
  if (!response.ok) {
    throw new Error("캘린더 동기화에 실패했습니다.");
  }
  return response.json();
}

export function calendarIcsUrl() {
  return `${API_BASE_URL}/calendar-events.ics`;
}
