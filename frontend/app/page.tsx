import { AlertCircle, CalendarDays, ClipboardCheck, Target } from "lucide-react";

import { getDashboard } from "@/lib/api";

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border bg-card p-4">
      <div className="text-sm text-muted-foreground">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  );
}

export default async function Home() {
  let dashboard = null;
  let error = null;

  try {
    dashboard = await getDashboard();
  } catch (err) {
    error = err instanceof Error ? err.message : "대시보드를 불러오지 못했습니다.";
  }

  const targetTrack = dashboard?.target_track ?? "온보딩 필요";
  const readiness = dashboard?.readiness?.[0];
  const weakestAxes = dashboard?.weakest_axes ?? [];

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-6 py-6">
        <header className="flex flex-col gap-3 border-b pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">취업준비 도우미</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-normal">이번 주 실행 계획</h1>
          </div>
          <div className="text-sm text-muted-foreground">지원 시작 목표: 2026년 9월</div>
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
          <Metric label="이번 주 상태" value="계획 전" />
        </section>

        <section className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
          <div className="rounded-md border bg-card">
            <div className="flex items-center gap-2 border-b px-5 py-4">
              <ClipboardCheck className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">이번 주 최우선 목표</h2>
            </div>
            <div className="grid gap-3 p-5">
              {["온보딩 입력 완료", "금융 IT 풀스택 트랙 점수 확인", "auto-invest README 1차 작성"].map((item) => (
                <div key={item} className="flex items-center justify-between rounded-md border p-3">
                  <span className="text-sm font-medium">{item}</span>
                  <span className="text-xs text-muted-foreground">todo</span>
                </div>
              ))}
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
              <div className="rounded-md bg-muted p-3">5월 말~6월: 기반 정리</div>
              <div className="rounded-md bg-muted p-3">7월: 취업 자료 제작</div>
              <div className="rounded-md bg-muted p-3">8월: 실전 지원 준비</div>
            </div>
          </div>
          <div className="rounded-md border bg-card p-5">
            <div className="flex items-center gap-2">
              <CalendarDays className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">일정</h2>
            </div>
            <p className="mt-4 text-sm text-muted-foreground">
              주간 계획, 공고 마감일, 자격증 시험일을 내부 캘린더와 .ics 내보내기로 연결할 예정입니다.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
