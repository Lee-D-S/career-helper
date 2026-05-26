"use client";

import type { FormEvent, InputHTMLAttributes } from "react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  createWeeklyPlan,
  deleteWeeklyPlan,
  getWeeklyPlans,
  updateTask,
  updateWeeklyPlan,
  type WeeklyPlan
} from "@/lib/api";

const planStatuses = ["active", "done", "paused", "archived"];

export default function WeeklyPlanPage() {
  const [plans, setPlans] = useState<WeeklyPlan[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  async function loadPlans() {
    setPlans(await getWeeklyPlans());
  }

  useEffect(() => {
    loadPlans().catch((error) => setStatus(error instanceof Error ? error.message : "주간 계획을 불러오지 못했습니다."));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const tasks = String(form.get("tasks") ?? "")
      .split("\n")
      .map((line) => line.trim() ? { title: line.trim(), category: "general", status: "todo" } : null)
      .filter(Boolean);

    try {
      await createWeeklyPlan({
        title: String(form.get("title") ?? ""),
        week_start: String(form.get("weekStart") ?? ""),
        week_end: String(form.get("weekEnd") ?? ""),
        status: "active",
        tasks
      });
      event.currentTarget.reset();
      await loadPlans();
      setStatus("주간 계획을 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "주간 계획 저장에 실패했습니다.");
    }
  }

  async function toggleTask(taskId: number, currentStatus: string) {
    try {
      await updateTask(taskId, { status: currentStatus === "done" ? "todo" : "done" });
      await loadPlans();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "작업 상태 저장에 실패했습니다.");
    }
  }

  async function changePlanStatus(planId: number, nextStatus: string) {
    try {
      await updateWeeklyPlan(planId, { status: nextStatus });
      await loadPlans();
      setStatus("주간 계획 상태를 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "주간 계획 상태 저장에 실패했습니다.");
    }
  }

  async function removePlan(planId: number) {
    try {
      await deleteWeeklyPlan(planId);
      await loadPlans();
      setStatus("주간 계획을 삭제했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "주간 계획 삭제에 실패했습니다.");
    }
  }

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-6">
        <header className="flex flex-col gap-3 border-b pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">실행 관리</p>
            <h1 className="mt-1 text-3xl font-semibold">주간 계획</h1>
          </div>
          <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/">
            대시보드
          </Link>
        </header>

        {status ? <div className="rounded-md border bg-card p-3 text-sm text-muted-foreground">{status}</div> : null}

        <form onSubmit={handleSubmit} className="grid gap-4 rounded-md border bg-card p-5">
          <div className="grid gap-4 md:grid-cols-3">
            <Input label="계획 제목" name="title" placeholder="이번 주 실행 계획" required />
            <Input label="시작일" name="weekStart" required type="date" />
            <Input label="종료일" name="weekEnd" required type="date" />
          </div>
          <label className="grid gap-2 text-sm font-medium">
            작업 항목
            <textarea
              className="min-h-28 rounded-md border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
              name="tasks"
              placeholder={"README 1차 작성\nSQL 20문제\n코딩테스트 Lv2 3문제"}
            />
          </label>
          <div>
            <Button type="submit">주간 계획 저장</Button>
          </div>
        </form>

        <section className="grid gap-4">
          {plans.map((plan) => (
            <article key={plan.id} className="rounded-md border bg-card">
              <div className="flex items-center justify-between border-b px-5 py-4">
                <div>
                  <h2 className="text-lg font-semibold">{plan.title}</h2>
                  <p className="text-sm text-muted-foreground">
                    {plan.week_start} ~ {plan.week_end}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    className="h-9 rounded-md border bg-background px-2 text-sm outline-none focus:border-primary"
                    onChange={(event) => changePlanStatus(plan.id, event.target.value)}
                    value={plan.status}
                  >
                    {planStatuses.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                  <Button onClick={() => removePlan(plan.id)} type="button" variant="secondary">
                    삭제
                  </Button>
                </div>
              </div>
              <div className="grid gap-3 p-5">
                {plan.tasks.map((task) => (
                  <button
                    className="flex items-center justify-between rounded-md border p-3 text-left transition-colors hover:bg-muted"
                    key={task.id}
                    onClick={() => toggleTask(task.id, task.status)}
                    type="button"
                  >
                    <span className="text-sm font-medium">{task.title}</span>
                    <span className="text-xs text-muted-foreground">{task.status}</span>
                  </button>
                ))}
              </div>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}

function Input(props: InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  const { label, ...rest } = props;
  return (
    <label className="grid gap-2 text-sm font-medium">
      {label}
      <input className="h-10 rounded-md border bg-background px-3 text-sm outline-none focus:border-primary" {...rest} />
    </label>
  );
}
