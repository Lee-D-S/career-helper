"use client";

import type { FormEvent, InputHTMLAttributes, TextareaHTMLAttributes } from "react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  calendarIcsUrl,
  createCalendarEvent,
  deleteCalendarEvent,
  getCalendarEvents,
  syncCalendarEvents,
  type CalendarEvent
} from "@/lib/api";

export default function CalendarPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  async function loadEvents() {
    setEvents(await getCalendarEvents());
  }

  useEffect(() => {
    loadEvents().catch((error) => setStatus(error instanceof Error ? error.message : "캘린더 일정을 불러오지 못했습니다."));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    try {
      await createCalendarEvent({
        title: String(form.get("title") ?? ""),
        description: String(form.get("description") ?? "") || null,
        start_at: String(form.get("startAt") ?? ""),
        end_at: String(form.get("endAt") ?? "") || null,
        event_type: String(form.get("eventType") ?? "task")
      });
      event.currentTarget.reset();
      await loadEvents();
      setStatus("일정을 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "일정 저장에 실패했습니다.");
    }
  }

  async function syncEvents() {
    try {
      const created = await syncCalendarEvents();
      await loadEvents();
      setStatus(`작업/공고에서 ${created.length}개 일정을 동기화했습니다.`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "캘린더 동기화에 실패했습니다.");
    }
  }

  async function removeEvent(eventId: number) {
    try {
      await deleteCalendarEvent(eventId);
      await loadEvents();
      setStatus("일정을 삭제했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "일정 삭제에 실패했습니다.");
    }
  }

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-6">
        <header className="flex flex-col gap-3 border-b pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">일정 관리</p>
            <h1 className="mt-1 text-3xl font-semibold">캘린더</h1>
          </div>
          <div className="flex gap-2">
            <Button onClick={syncEvents} type="button" variant="secondary">
              작업/공고 동기화
            </Button>
            <a className="rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground" href={calendarIcsUrl()}>
              .ics 내보내기
            </a>
            <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/">
              대시보드
            </Link>
          </div>
        </header>

        {status ? <div className="rounded-md border bg-card p-3 text-sm text-muted-foreground">{status}</div> : null}

        <form onSubmit={handleSubmit} className="grid gap-4 rounded-md border bg-card p-5">
          <div className="grid gap-4 md:grid-cols-3">
            <Input label="제목" name="title" required />
            <Input label="시작" name="startAt" required type="datetime-local" />
            <Input label="종료" name="endAt" type="datetime-local" />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="grid gap-2 text-sm font-medium">
              유형
              <select className="h-10 rounded-md border bg-background px-3 text-sm outline-none focus:border-primary" name="eventType">
                <option value="task">작업</option>
                <option value="job_deadline">공고 마감</option>
                <option value="certificate_exam">자격증 시험</option>
                <option value="language_test">어학 시험</option>
                <option value="review">회고</option>
              </select>
            </label>
          </div>
          <Textarea label="설명" name="description" />
          <div>
            <Button type="submit">일정 저장</Button>
          </div>
        </form>

        <section className="grid gap-3">
          {events.map((event) => (
            <article key={event.id} className="rounded-md border bg-card p-4">
              <div className="flex flex-col gap-1 md:flex-row md:items-center md:justify-between">
                <div>
                  <h2 className="text-sm font-semibold">{event.title}</h2>
                  <p className="text-sm text-muted-foreground">
                    {formatDateTime(event.start_at)} {event.end_at ? `~ ${formatDateTime(event.end_at)}` : ""}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">{event.event_type}</span>
                  <Button onClick={() => removeEvent(event.id)} type="button" variant="secondary">
                    삭제
                  </Button>
                </div>
              </div>
              {event.description ? <p className="mt-3 text-sm text-muted-foreground">{event.description}</p> : null}
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
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
