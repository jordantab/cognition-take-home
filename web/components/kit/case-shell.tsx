import Link from "next/link";
import { ChevronLeft } from "lucide-react";

import type { CaseRow, State } from "@/lib/types";
import { dateTime } from "@/lib/format";

import { PriorityBadge, StatusBadge } from "./status-badge";
import { RiskScore } from "./risk-score";
import { SlaClock } from "./sla-clock";

/** Two-column case workspace shared by every case type. */
export function CaseShell({
  caseRow,
  states,
  backHref,
  backLabel,
  main,
  rail,
}: {
  caseRow: CaseRow;
  states: State[];
  backHref: string;
  backLabel: string;
  main: React.ReactNode;
  rail: React.ReactNode;
}) {
  return (
    <div className="flex min-h-full flex-col">
      <div className="border-b px-6 py-4">
        <Link
          href={backHref}
          className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
        >
          <ChevronLeft className="size-3.5" />
          {backLabel}
        </Link>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <span className="font-mono text-sm text-muted-foreground">
            {caseRow.reference}
          </span>
          <h1 className="text-xl font-semibold tracking-tight">
            {caseRow.title}
          </h1>
          <StatusBadge status={caseRow.status} states={states} />
          <PriorityBadge priority={caseRow.priority} />
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
          <span>Opened {dateTime(caseRow.opened_at)}</span>
          <SlaClock
            hoursRemaining={caseRow.hours_remaining}
            overdue={caseRow.overdue}
            closed={Boolean(caseRow.closed_at)}
          />
          <span className="flex items-center gap-1.5">
            Risk <RiskScore score={caseRow.risk_score} />
          </span>
        </div>
      </div>

      <div className="grid flex-1 gap-6 p-6 xl:grid-cols-[minmax(0,1fr)_22rem]">
        <div className="min-w-0 space-y-6">{main}</div>
        <div className="space-y-4">{rail}</div>
      </div>
    </div>
  );
}
