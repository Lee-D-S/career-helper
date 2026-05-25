const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export type AxisScore = {
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
