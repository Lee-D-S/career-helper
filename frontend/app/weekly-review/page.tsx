"use client";

import type { FormEvent, TextareaHTMLAttributes } from "react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { createWeeklyReview, getWeeklyPlans, getWeeklyReviews, type WeeklyPlan, type WeeklyReview } from "@/lib/api";

export default function WeeklyReviewPage() {
  const [plans, setPlans] = useState<WeeklyPlan[]>([]);
  const [reviews, setReviews] = useState<WeeklyReview[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  async function loadData() {
    const [planData, reviewData] = await Promise.all([getWeeklyPlans(), getWeeklyReviews()]);
    setPlans(planData);
    setReviews(reviewData);
  }

  useEffect(() => {
    loadData().catch((error) => setStatus(error instanceof Error ? error.message : "회고 데이터를 불러오지 못했습니다."));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    try {
      await createWeeklyReview({
        weekly_plan_id: Number(form.get("weeklyPlanId")),
        blockers: String(form.get("blockers") ?? "") || null,
        priority_adjustments: String(form.get("priorityAdjustments") ?? "") || null,
        score_changes: String(form.get("scoreChanges") ?? "") || null,
        summary: String(form.get("summary") ?? "") || null
      });
      event.currentTarget.reset();
      await loadData();
      setStatus("주간 회고를 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "주간 회고 저장에 실패했습니다.");
    }
  }

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-6 py-6">
        <header className="flex flex-col gap-3 border-b pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">계획 조정</p>
            <h1 className="mt-1 text-3xl font-semibold">주간 회고</h1>
          </div>
          <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/">
            대시보드
          </Link>
        </header>

        {status ? <div className="rounded-md border bg-card p-3 text-sm text-muted-foreground">{status}</div> : null}

        <form onSubmit={handleSubmit} className="grid gap-4 rounded-md border bg-card p-5">
          <label className="grid gap-2 text-sm font-medium">
            주간 계획
            <select className="h-10 rounded-md border bg-background px-3 text-sm outline-none focus:border-primary" name="weeklyPlanId" required>
              <option value="">선택</option>
              {plans.map((plan) => (
                <option key={plan.id} value={plan.id}>
                  {plan.title} ({plan.week_start} ~ {plan.week_end})
                </option>
              ))}
            </select>
          </label>
          <Textarea label="미완료 원인/막힌 점" name="blockers" />
          <Textarea label="다음 주 우선순위 조정" name="priorityAdjustments" />
          <Textarea label="준비도 점수 변화" name="scoreChanges" />
          <Textarea label="요약" name="summary" />
          <div>
            <Button type="submit">회고 저장</Button>
          </div>
        </form>

        <section className="grid gap-3">
          {reviews.map((review) => (
            <article key={review.id} className="rounded-md border bg-card p-4">
              <div className="flex justify-between text-sm">
                <span className="font-medium">주간 계획 #{review.weekly_plan_id}</span>
                <span className="text-muted-foreground">실행률 {review.completion_rate}%</span>
              </div>
              {review.summary ? <p className="mt-3 text-sm">{review.summary}</p> : null}
              {review.priority_adjustments ? (
                <p className="mt-2 text-sm text-muted-foreground">다음 조정: {review.priority_adjustments}</p>
              ) : null}
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}

function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string }) {
  const { label, ...rest } = props;
  return (
    <label className="grid gap-2 text-sm font-medium">
      {label}
      <textarea className="min-h-20 rounded-md border bg-background px-3 py-2 text-sm outline-none focus:border-primary" {...rest} />
    </label>
  );
}
