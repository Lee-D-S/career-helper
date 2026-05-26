"use client";

import type { FormEvent, InputHTMLAttributes } from "react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  createRoadmap,
  deleteRoadmap,
  getRoadmaps,
  updateRoadmap,
  updateRoadmapItem,
  type Roadmap
} from "@/lib/api";

const statuses = ["todo", "active", "done", "paused", "archived"];

export default function RoadmapPage() {
  const [roadmaps, setRoadmaps] = useState<Roadmap[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  async function loadRoadmaps() {
    setRoadmaps(await getRoadmaps());
  }

  useEffect(() => {
    loadRoadmaps().catch((error) => setStatus(error instanceof Error ? error.message : "로드맵을 불러오지 못했습니다."));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const items = String(form.get("items") ?? "")
      .split("\n")
      .map((line, index) => line.trim() ? { title: line.trim(), priority: index + 1, status: "todo" } : null)
      .filter(Boolean);

    try {
      await createRoadmap({
        title: String(form.get("title") ?? ""),
        start_date: String(form.get("startDate") ?? "") || null,
        end_date: String(form.get("endDate") ?? "") || null,
        status: "active",
        items
      });
      event.currentTarget.reset();
      await loadRoadmaps();
      setStatus("로드맵을 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "로드맵 저장에 실패했습니다.");
    }
  }

  async function changeRoadmapStatus(roadmapId: number, nextStatus: string) {
    try {
      await updateRoadmap(roadmapId, { status: nextStatus });
      await loadRoadmaps();
      setStatus("로드맵 상태를 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "로드맵 상태 저장에 실패했습니다.");
    }
  }

  async function removeRoadmap(roadmapId: number) {
    try {
      await deleteRoadmap(roadmapId);
      await loadRoadmaps();
      setStatus("로드맵을 삭제했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "로드맵 삭제에 실패했습니다.");
    }
  }

  async function changeItemStatus(itemId: number, nextStatus: string) {
    try {
      await updateRoadmapItem(itemId, { status: nextStatus });
      await loadRoadmaps();
      setStatus("로드맵 항목 상태를 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "로드맵 항목 상태 저장에 실패했습니다.");
    }
  }

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-6">
        <header className="flex flex-col gap-3 border-b pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">전체 계획</p>
            <h1 className="mt-1 text-3xl font-semibold">로드맵</h1>
          </div>
          <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/">
            대시보드
          </Link>
        </header>

        {status ? <div className="rounded-md border bg-card p-3 text-sm text-muted-foreground">{status}</div> : null}

        <form onSubmit={handleSubmit} className="grid gap-4 rounded-md border bg-card p-5">
          <div className="grid gap-4 md:grid-cols-3">
            <Input label="로드맵 제목" name="title" placeholder="6월 기반 정리" required />
            <Input label="시작일" name="startDate" type="date" />
            <Input label="종료일" name="endDate" type="date" />
          </div>
          <label className="grid gap-2 text-sm font-medium">
            목표 항목
            <textarea
              className="min-h-28 rounded-md border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
              name="items"
              placeholder={"auto-invest README 1차 작성\nSQL 기본기 복구\n코딩테스트 Lv2 연습"}
            />
          </label>
          <div>
            <Button type="submit">로드맵 저장</Button>
          </div>
        </form>

        <section className="grid gap-4">
          {roadmaps.map((roadmap) => (
            <article key={roadmap.id} className="rounded-md border bg-card">
              <div className="flex items-center justify-between border-b px-5 py-4">
                <div>
                  <h2 className="text-lg font-semibold">{roadmap.title}</h2>
                  <p className="text-sm text-muted-foreground">
                    {roadmap.start_date ?? "-"} ~ {roadmap.end_date ?? "-"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    className="h-9 rounded-md border bg-background px-2 text-sm outline-none focus:border-primary"
                    onChange={(event) => changeRoadmapStatus(roadmap.id, event.target.value)}
                    value={roadmap.status}
                  >
                    {statuses.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                  <Button onClick={() => removeRoadmap(roadmap.id)} type="button" variant="secondary">
                    삭제
                  </Button>
                </div>
              </div>
              <div className="grid gap-3 p-5">
                {roadmap.items.map((item) => (
                  <div key={item.id} className="flex items-center justify-between rounded-md border p-3">
                    <span className="text-sm font-medium">{item.title}</span>
                    <select
                      className="h-8 rounded-md border bg-background px-2 text-xs outline-none focus:border-primary"
                      onChange={(event) => changeItemStatus(item.id, event.target.value)}
                      value={item.status}
                    >
                      {statuses.map((statusItem) => (
                        <option key={statusItem} value={statusItem}>
                          {statusItem}
                        </option>
                      ))}
                    </select>
                  </div>
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
