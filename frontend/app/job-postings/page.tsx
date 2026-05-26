"use client";

import type { FormEvent, InputHTMLAttributes, TextareaHTMLAttributes } from "react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  analyzeJobPosting,
  createJobPosting,
  deleteJobPosting,
  getJobPostings,
  updateJobPosting,
  type JobPosting
} from "@/lib/api";

const jobStatuses = ["saved", "ready", "applied", "rejected", "interviewing", "offer", "archived"];

export default function JobPostingsPage() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  async function loadJobs() {
    setJobs(await getJobPostings());
  }

  useEffect(() => {
    loadJobs().catch((error) => setStatus(error instanceof Error ? error.message : "공고를 불러오지 못했습니다."));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    try {
      await createJobPosting({
        company_name: String(form.get("companyName") ?? "") || null,
        position_title: String(form.get("positionTitle") ?? "") || null,
        source_url: String(form.get("sourceUrl") ?? "") || null,
        raw_content: String(form.get("rawContent") ?? "") || null,
        deadline: String(form.get("deadline") ?? "") || null,
        status: "saved"
      });
      event.currentTarget.reset();
      await loadJobs();
      setStatus("공고를 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "공고 저장에 실패했습니다.");
    }
  }

  async function analyze(jobId: number) {
    try {
      await analyzeJobPosting(jobId);
      await loadJobs();
      setStatus("공고 분석을 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "공고 분석에 실패했습니다.");
    }
  }

  async function changeStatus(jobId: number, nextStatus: string) {
    try {
      await updateJobPosting(jobId, { status: nextStatus });
      await loadJobs();
      setStatus("공고 상태를 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "공고 상태 저장에 실패했습니다.");
    }
  }

  async function removeJob(jobId: number) {
    try {
      await deleteJobPosting(jobId);
      await loadJobs();
      setStatus("공고를 삭제했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "공고 삭제에 실패했습니다.");
    }
  }

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-6">
        <header className="flex flex-col gap-3 border-b pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">지원 관리</p>
            <h1 className="mt-1 text-3xl font-semibold">공고 저장/분석</h1>
          </div>
          <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/">
            대시보드
          </Link>
        </header>

        {status ? <div className="rounded-md border bg-card p-3 text-sm text-muted-foreground">{status}</div> : null}

        <form onSubmit={handleSubmit} className="grid gap-4 rounded-md border bg-card p-5">
          <div className="grid gap-4 md:grid-cols-2">
            <Input label="회사명" name="companyName" />
            <Input label="직무명" name="positionTitle" />
            <Input label="공고 URL" name="sourceUrl" />
            <Input label="마감일" name="deadline" type="date" />
          </div>
          <Textarea label="공고 본문" name="rawContent" />
          <div>
            <Button type="submit">공고 저장</Button>
          </div>
        </form>

        <section className="grid gap-4">
          {jobs.map((job) => (
            <article key={job.id} className="rounded-md border bg-card">
              <div className="flex flex-col gap-2 border-b px-5 py-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <h2 className="text-lg font-semibold">{job.company_name || "회사명 미입력"}</h2>
                  <p className="text-sm text-muted-foreground">
                    {job.position_title || "직무명 미입력"} · 마감 {job.deadline || "-"} · {job.status}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {job.fit_score != null ? <span className="text-sm text-muted-foreground">적합도 {job.fit_score}</span> : null}
                  <select
                    className="h-9 rounded-md border bg-background px-2 text-sm outline-none focus:border-primary"
                    onChange={(event) => changeStatus(job.id, event.target.value)}
                    value={job.status}
                  >
                    {jobStatuses.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                  <Button onClick={() => analyze(job.id)} type="button">
                    분석
                  </Button>
                  <Button onClick={() => removeJob(job.id)} type="button" variant="secondary">
                    삭제
                  </Button>
                </div>
              </div>
              <div className="grid gap-4 p-5">
                {job.summary ? <p className="text-sm">{job.summary}</p> : <p className="text-sm text-muted-foreground">분석 전입니다.</p>}
                {job.required_skills.length ? (
                  <div className="flex flex-wrap gap-2">
                    {job.required_skills.map((skill) => (
                      <span key={skill} className="rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground">
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : null}
                {job.recommended_actions.length ? (
                  <ul className="grid gap-2 text-sm text-muted-foreground">
                    {job.recommended_actions.map((action) => (
                      <li key={action}>- {action}</li>
                    ))}
                  </ul>
                ) : null}
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

function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string }) {
  const { label, ...rest } = props;
  return (
    <label className="grid gap-2 text-sm font-medium">
      {label}
      <textarea className="min-h-32 rounded-md border bg-background px-3 py-2 text-sm outline-none focus:border-primary" {...rest} />
    </label>
  );
}
