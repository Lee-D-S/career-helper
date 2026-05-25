"use client";

import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { type DashboardSummary, getDashboard, updateScore } from "@/lib/api";

export default function ReadinessPage() {
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  async function loadDashboard() {
    const data = await getDashboard();
    setDashboard(data);
  }

  useEffect(() => {
    loadDashboard().catch((error) => setStatus(error instanceof Error ? error.message : "준비도를 불러오지 못했습니다."));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const scoreId = Number(form.get("scoreId"));
    const score = Number(form.get("score"));
    const targetScore = Number(form.get("targetScore"));
    const evidence = String(form.get("evidence") ?? "");

    try {
      await updateScore(scoreId, {
        score,
        target_score: Number.isNaN(targetScore) ? undefined : targetScore,
        evidence: evidence || null
      });
      await loadDashboard();
      setStatus("저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "저장에 실패했습니다.");
    }
  }

  const tracks = dashboard?.readiness ?? [];

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-6">
        <header className="flex flex-col gap-3 border-b pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">진단 관리</p>
            <h1 className="mt-1 text-3xl font-semibold">역량 점수 수정</h1>
          </div>
          <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/">
            대시보드
          </Link>
        </header>

        {status ? <div className="rounded-md border bg-card p-3 text-sm text-muted-foreground">{status}</div> : null}

        {tracks.length ? (
          <div className="grid gap-6">
            {tracks.map((track) => (
              <section key={track.id} className="rounded-md border bg-card">
                <div className="flex items-center justify-between border-b px-5 py-4">
                  <div>
                    <h2 className="text-lg font-semibold">{track.name}</h2>
                    <p className="text-sm text-muted-foreground">가중 준비도 {track.weighted_score}/5</p>
                  </div>
                  <span className="text-sm text-muted-foreground">우선순위 {track.priority}</span>
                </div>

                <div className="divide-y">
                  {track.scores.map((item) => (
                    <form key={item.id} onSubmit={handleSubmit} className="grid gap-3 p-4 md:grid-cols-[1.2fr_120px_120px_1fr_auto] md:items-end">
                      <input name="scoreId" type="hidden" value={item.id} />
                      <label className="grid gap-2 text-sm font-medium">
                        역량
                        <input className="h-10 rounded-md border bg-muted px-3 text-sm" readOnly value={item.axis} />
                      </label>
                      <label className="grid gap-2 text-sm font-medium">
                        현재
                        <input
                          className="h-10 rounded-md border bg-background px-3 text-sm outline-none focus:border-primary"
                          defaultValue={item.score}
                          max={5}
                          min={0}
                          name="score"
                          step="0.5"
                          type="number"
                        />
                      </label>
                      <label className="grid gap-2 text-sm font-medium">
                        목표
                        <input
                          className="h-10 rounded-md border bg-background px-3 text-sm outline-none focus:border-primary"
                          defaultValue={item.target_score}
                          max={5}
                          min={0}
                          name="targetScore"
                          step="0.5"
                          type="number"
                        />
                      </label>
                      <label className="grid gap-2 text-sm font-medium">
                        증거/메모
                        <input
                          className="h-10 rounded-md border bg-background px-3 text-sm outline-none focus:border-primary"
                          defaultValue={item.evidence ?? ""}
                          name="evidence"
                          placeholder="프로젝트, 인턴, 학습 기록"
                        />
                      </label>
                      <Button type="submit">저장</Button>
                    </form>
                  ))}
                </div>
              </section>
            ))}
          </div>
        ) : (
          <section className="rounded-md border bg-card p-5">
            <p className="text-sm text-muted-foreground">온보딩을 먼저 완료하면 역량 점수를 수정할 수 있습니다.</p>
            <Link className="mt-4 inline-flex rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground" href="/onboarding">
              온보딩 입력
            </Link>
          </section>
        )}
      </div>
    </main>
  );
}
