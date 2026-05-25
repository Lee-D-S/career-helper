"use client";

import type { FormEvent, InputHTMLAttributes, TextareaHTMLAttributes } from "react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { createDailyCheckIn, getDailyCheckIns, type DailyCheckIn } from "@/lib/api";

export default function CheckInPage() {
  const [checkIns, setCheckIns] = useState<DailyCheckIn[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  async function loadCheckIns() {
    setCheckIns(await getDailyCheckIns());
  }

  useEffect(() => {
    loadCheckIns().catch((error) => setStatus(error instanceof Error ? error.message : "체크인을 불러오지 못했습니다."));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    try {
      await createDailyCheckIn({
        date: String(form.get("date") ?? ""),
        actual_hours: Number(form.get("actualHours")) || 0,
        completed_work: String(form.get("completedWork") ?? ""),
        blockers: String(form.get("blockers") ?? "") || null
      });
      event.currentTarget.reset();
      await loadCheckIns();
      setStatus("체크인을 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "체크인 저장에 실패했습니다.");
    }
  }

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-6 py-6">
        <header className="flex flex-col gap-3 border-b pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">실행 기록</p>
            <h1 className="mt-1 text-3xl font-semibold">일일 체크인</h1>
          </div>
          <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/">
            대시보드
          </Link>
        </header>

        {status ? <div className="rounded-md border bg-card p-3 text-sm text-muted-foreground">{status}</div> : null}

        <form onSubmit={handleSubmit} className="grid gap-4 rounded-md border bg-card p-5">
          <div className="grid gap-4 md:grid-cols-2">
            <Input label="날짜" name="date" required type="date" />
            <Input label="실제 투입 시간" name="actualHours" required step="0.5" type="number" />
          </div>
          <Textarea label="완료한 작업" name="completedWork" required />
          <Textarea label="막힌 점" name="blockers" />
          <div>
            <Button type="submit">체크인 저장</Button>
          </div>
        </form>

        <section className="grid gap-3">
          {checkIns.map((checkIn) => (
            <article key={checkIn.id} className="rounded-md border bg-card p-4">
              <div className="flex justify-between text-sm">
                <span className="font-medium">{checkIn.date}</span>
                <span className="text-muted-foreground">{checkIn.actual_hours}시간</span>
              </div>
              <p className="mt-3 text-sm">{checkIn.completed_work}</p>
              {checkIn.blockers ? <p className="mt-2 text-sm text-muted-foreground">막힌 점: {checkIn.blockers}</p> : null}
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

function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string }) {
  const { label, ...rest } = props;
  return (
    <label className="grid gap-2 text-sm font-medium">
      {label}
      <textarea className="min-h-24 rounded-md border bg-background px-3 py-2 text-sm outline-none focus:border-primary" {...rest} />
    </label>
  );
}
