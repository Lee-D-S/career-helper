"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { createAiSuggestion, getAiPlans, updateAiPlanDecision, type AiPlan } from "@/lib/api";

const suggestionTypes = [
  { label: "로드맵", value: "roadmap" },
  { label: "주간 계획", value: "weekly_plan" },
  { label: "주간 회고", value: "weekly_review" },
  { label: "공고 분석", value: "job_posting" }
];

export default function AiSuggestionsPage() {
  const [plans, setPlans] = useState<AiPlan[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  async function loadPlans() {
    setPlans(await getAiPlans());
  }

  useEffect(() => {
    loadPlans().catch((error) => setStatus(error instanceof Error ? error.message : "AI 제안을 불러오지 못했습니다."));
  }, []);

  async function generate(planType: string) {
    try {
      await createAiSuggestion(planType);
      await loadPlans();
      setStatus("AI 제안을 생성했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "AI 제안 생성에 실패했습니다.");
    }
  }

  async function decide(planId: number, decisionStatus: string) {
    try {
      await updateAiPlanDecision(planId, decisionStatus);
      await loadPlans();
      setStatus("AI 제안 상태를 저장했습니다.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "AI 제안 상태 저장에 실패했습니다.");
    }
  }

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-6">
        <header className="flex flex-col gap-3 border-b pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">MockProvider</p>
            <h1 className="mt-1 text-3xl font-semibold">AI 제안</h1>
          </div>
          <Link className="rounded-md bg-muted px-3 py-2 text-sm font-medium" href="/">
            대시보드
          </Link>
        </header>

        {status ? <div className="rounded-md border bg-card p-3 text-sm text-muted-foreground">{status}</div> : null}

        <section className="grid gap-3 rounded-md border bg-card p-5 md:grid-cols-4">
          {suggestionTypes.map((type) => (
            <Button key={type.value} onClick={() => generate(type.value)} type="button" variant="secondary">
              {type.label} 생성
            </Button>
          ))}
        </section>

        <section className="grid gap-4">
          {plans.map((plan) => (
            <article key={plan.id} className="rounded-md border bg-card">
              <div className="flex flex-col gap-2 border-b px-5 py-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <h2 className="text-lg font-semibold">{plan.plan_type}</h2>
                  <p className="text-sm text-muted-foreground">{plan.user_explanation}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">{plan.decision_status}</span>
                  <Button onClick={() => decide(plan.id, "accepted")} type="button">
                    승인/반영
                  </Button>
                  <Button onClick={() => decide(plan.id, "rejected")} type="button" variant="secondary">
                    거절
                  </Button>
                </div>
              </div>
              {plan.applied_resource_type && plan.applied_resource_id ? (
                <div className="border-b px-5 py-3 text-sm text-muted-foreground">
                  반영됨: {plan.applied_resource_type} #{plan.applied_resource_id}
                </div>
              ) : null}
              <pre className="overflow-auto p-5 text-sm text-muted-foreground">
                {JSON.stringify(plan.parsed_json, null, 2)}
              </pre>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}
