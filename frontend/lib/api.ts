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
