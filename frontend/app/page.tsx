import { AlertCircle, CalendarDays, ClipboardCheck, Target } from "lucide-react";
import Link from "next/link";

import {
  type DailyCheckIn,
  type DashboardSummary,
  getDailyCheckIns,
  getDashboard,
  getRoadmaps,
  getWeeklyPlans,
  type Roadmap,
  type WeeklyPlan
} from "@/lib/api";

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border bg-card p-4">
      <div className="text-sm text-muted-foreground">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  );
}

export default async function Home() {
  let dashboard: DashboardSummary | null = null;
  let roadmaps: Roadmap[] = [];
  let weeklyPlans: WeeklyPlan[] = [];
  let checkIns: DailyCheckIn[] = [];
  let error: string | null = null;

  try {
    const [dashboardData, roadmapData, weeklyPlanData, checkInData] = await Promise.all([
      getDashboard(),
      getRoadmaps(),
      getWeeklyPlans(),
      getDailyCheckIns()
    ]);
    dashboard = dashboardData;
    roadmaps = roadmapData;
    weeklyPlans = weeklyPlanData;
    checkIns = checkInData;
  } catch (err) {
    error = err instanceof Error ? err.message : "대시보드를 불러오지 못했습니다.";
  }

  const targetTrack = dashboard?.target_track ?? "온보딩 필요";
  const readiness = dashboard?.readiness?.[0];
  const weakestAxes = dashboard?.weakest_axes ?? [];
  const currentPlan = weeklyPlans[0];
  const currentRoadmap = roadmaps[0];
  const latestCheckIn = checkIns[0];

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-6 py-6">
        <header className="flex flex-col gap-3 border-b pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">취업준비 도우미</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-normal">이번 주 실행 계획</h1>
          </div>
          <div className="flex gap-2">
            <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/onboarding">
              온보딩
            </Link>
            <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/roadmap">
              로드맵
            </Link>
            <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/weekly-plan">
              주간 계획
            </Link>
            <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/check-in">
              체크인
            </Link>
            <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/weekly-review">
              회고
            </Link>
            <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/ai-suggestions">
              AI 제안
            </Link>
            <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/job-postings">
              공고
            </Link>
            <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/calendar">
              캘린더
            </Link>
            <Link className="rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground" href="/readiness">
              역량 점수
            </Link>
          </div>
        </header>

        {error ? (
          <section className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            API 연결 전입니다. 백엔드를 실행한 뒤 대시보드 데이터가 표시됩니다.
          </section>
        ) : null}

        <section className="grid gap-4 md:grid-cols-4">
          <Metric label="목표 직무" value={targetTrack} />
          <Metric label="준비도 점수" value={readiness ? `${readiness.weighted_score}/5` : "-"} />
          <Metric label="부족 역량" value={weakestAxes[0]?.axis ?? "-"} />
          <Metric label="최근 체크인" value={latestCheckIn ? `${latestCheckIn.actual_hours}h` : "없음"} />
        </section>

        <section className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
          <div className="rounded-md border bg-card">
            <div className="flex items-center gap-2 border-b px-5 py-4">
              <ClipboardCheck className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">이번 주 최우선 목표</h2>
            </div>
            <div className="grid gap-3 p-5">
              {(currentPlan?.tasks.length ? currentPlan.tasks : []).map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded-md border p-3">
                  <span className="text-sm font-medium">{item.title}</span>
                  <span className="text-xs text-muted-foreground">{item.status}</span>
                </div>
              ))}
              {!currentPlan?.tasks.length ? (
                <p className="text-sm text-muted-foreground">주간 계획을 만들면 최우선 작업이 표시됩니다.</p>
              ) : null}
            </div>
          </div>

          <div className="rounded-md border bg-card">
            <div className="flex items-center gap-2 border-b px-5 py-4">
              <AlertCircle className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">부족 역량 Top 3</h2>
            </div>
            <div className="grid gap-3 p-5">
              {weakestAxes.length ? (
                weakestAxes.map((item) => (
                  <div key={item.axis} className="rounded-md border p-3">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">{item.axis}</span>
                      <span>{item.score}/5</span>
                    </div>
                    <div className="mt-2 h-2 rounded bg-muted">
                      <div className="h-2 rounded bg-primary" style={{ width: `${(item.score / 5) * 100}%` }} />
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">온보딩을 완료하면 부족 역량이 표시됩니다.</p>
              )}
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2">
          <div className="rounded-md border bg-card p-5">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">로드맵</h2>
            </div>
            <div className="mt-4 space-y-3 text-sm">
              {currentRoadmap?.items.length ? (
                currentRoadmap.items.map((item) => (
                  <div key={item.id} className="rounded-md bg-muted p-3">
                    {item.title}
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">로드맵을 만들면 월간 목표가 표시됩니다.</p>
              )}
            </div>
          </div>
          <div className="rounded-md border bg-card p-5">
            <div className="flex items-center gap-2">
              <CalendarDays className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">최근 체크인</h2>
            </div>
            {latestCheckIn ? (
              <div className="mt-4 space-y-2 text-sm">
                <p className="font-medium">
                  {latestCheckIn.date} · {latestCheckIn.actual_hours}시간
                </p>
                <p className="text-muted-foreground">{latestCheckIn.completed_work}</p>
                {latestCheckIn.blockers ? <p className="text-muted-foreground">막힌 점: {latestCheckIn.blockers}</p> : null}
              </div>
            ) : (
              <p className="mt-4 text-sm text-muted-foreground">일일 체크인을 남기면 최근 실행 기록이 표시됩니다.</p>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
