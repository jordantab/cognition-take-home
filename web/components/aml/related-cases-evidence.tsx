import Link from "next/link";

import { StatusBadge } from "@/components/kit/status-badge";
import type { EvidenceProps } from "@/components/kit/evidence-tabs";
import { day } from "@/lib/format";

export function RelatedCasesEvidence({ detail, states }: EvidenceProps) {
  if (detail.related_cases.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No other alerts on this customer.
      </p>
    );
  }

  return (
    <ul className="divide-y rounded-lg border">
      {detail.related_cases.map((related) => (
        <li key={related.id}>
          <Link
            href={`/aml/${related.id}`}
            className="flex flex-wrap items-center gap-3 px-4 py-3 hover:bg-muted/50"
          >
            <span className="font-mono text-xs text-muted-foreground">
              {related.reference}
            </span>
            <span className="min-w-0 flex-1 truncate text-sm">
              {related.title}
            </span>
            <StatusBadge status={related.status} states={states} />
            <span className="text-xs text-muted-foreground">
              {day(related.opened_at)}
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
