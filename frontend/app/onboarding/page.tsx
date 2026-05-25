"use client";

import type { FormEvent, InputHTMLAttributes, TextareaHTMLAttributes } from "react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { submitOnboarding } from "@/lib/api";

export default function OnboardingPage() {
  const router = useRouter();
  const [status, setStatus] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const targetRoles = String(form.get("targetRoles") ?? "")
      .split(",")
      .map((role) => role.trim())
      .filter(Boolean);

    const payload = {
      user: {
        name: String(form.get("name") ?? "default"),
        school: String(form.get("school") ?? ""),
        major: String(form.get("major") ?? ""),
        current_semester: String(form.get("currentSemester") ?? ""),
        expected_graduation_date: String(form.get("graduationDate") ?? "") || null,
        overall_gpa: Number(form.get("overallGpa")) || null,
        major_gpa: Number(form.get("majorGpa")) || null,
        total_credits: Number(form.get("totalCredits")) || null
      },
      target_roles: targetRoles,
      target_application_start_date: String(form.get("applicationStartDate") ?? "") || null,
      weekday_available_hours: Number(form.get("weekdayHours")) || null,
      weekend_available_hours: Number(form.get("weekendHours")) || null,
      primary_language: String(form.get("primaryLanguage") ?? ""),
      backend_experience: String(form.get("backendExperience") ?? ""),
      db_experience: String(form.get("dbExperience") ?? ""),
      infra_experience: String(form.get("infraExperience") ?? ""),
      coding_test_level: String(form.get("codingTestLevel") ?? ""),
      raw_notes: String(form.get("rawNotes") ?? "")
    };

    try {
      await submitOnboarding(payload);
      setStatus("온보딩을 저장했습니다. 대시보드로 돌아가 준비도를 확인하세요.");
      router.push("/");
      router.refresh();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "온보딩 저장에 실패했습니다.");
    }
  }

  return (
    <main className="min-h-screen">
      <form onSubmit={handleSubmit} className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-6 py-6">
        <header className="border-b pb-5">
          <p className="text-sm font-medium text-muted-foreground">초기 진단</p>
          <h1 className="mt-1 text-3xl font-semibold">온보딩 입력</h1>
        </header>

        <section className="grid gap-4 rounded-md border bg-card p-5 md:grid-cols-2">
          <Input name="name" label="이름" defaultValue="default" />
          <Input name="school" label="학교" />
          <Input name="major" label="전공" />
          <Input name="currentSemester" label="현재 학기" placeholder="4-1" />
          <Input name="graduationDate" label="졸업 예정일" type="date" />
          <Input name="applicationStartDate" label="지원 시작 목표일" type="date" />
          <Input name="overallGpa" label="전체 학점" type="number" step="0.01" />
          <Input name="majorGpa" label="전공 학점" type="number" step="0.01" />
          <Input name="totalCredits" label="총 이수 학점" type="number" />
          <Input name="targetRoles" label="목표 직무" defaultValue="금융 IT 풀스택, 백엔드/서버, AI, 데이터" />
          <Input name="weekdayHours" label="평일 가능 시간" type="number" step="0.5" />
          <Input name="weekendHours" label="주말 가능 시간" type="number" step="0.5" />
        </section>

        <section className="grid gap-4 rounded-md border bg-card p-5">
          <Input name="primaryLanguage" label="주 언어" placeholder="Python" />
          <Textarea name="backendExperience" label="백엔드/API 경험" />
          <Textarea name="dbExperience" label="DB/SQL 경험" />
          <Textarea name="infraExperience" label="인프라/배포 경험" />
          <Input name="codingTestLevel" label="코딩테스트 수준" placeholder="프로그래머스 Lv1~2" />
          <Textarea name="rawNotes" label="인턴/프로젝트/공모전 메모" />
        </section>

        <div className="flex items-center gap-3">
          <Button type="submit">저장</Button>
          {status ? <span className="text-sm text-muted-foreground">{status}</span> : null}
        </div>
      </form>
    </main>
  );
}

function Input(props: InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  const { label, className, ...rest } = props;
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
