import type { CaseRow, SummaryField } from "@/lib/types";
import { money, titleCase } from "@/lib/format";

import { RiskScore } from "./risk-score";
import { TagBadge } from "./status-badge";

const RISK_RATING_LABEL: Record<string, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

/** Key/value summary rendered from the case type's declared summary fields. */
export function SummaryList({
  caseRow,
  fields,
}: {
  caseRow: CaseRow;
  fields: SummaryField[];
}) {
  return (
    <dl className="grid gap-3 sm:grid-cols-2">
      {fields.map((field) => (
        <div key={field.key} className="min-w-0">
          <dt className="text-xs text-muted-foreground">{field.label}</dt>
          <dd className="mt-0.5 text-sm">
            <SummaryValue caseRow={caseRow} field={field} />
          </dd>
        </div>
      ))}
    </dl>
  );
}

function SummaryValue({
  caseRow,
  field,
}: {
  caseRow: CaseRow;
  field: SummaryField;
}) {
  const raw =
    field.key in caseRow
      ? caseRow[field.key as keyof CaseRow]
      : caseRow.extra?.[field.key];

  switch (field.type) {
    case "money":
      return <span className="tabular-nums">{money(Number(raw ?? 0), true)}</span>;
    case "tag":
      return (
        <TagBadge
          label={String(caseRow.extra?.[`${field.key}_label`] ?? raw ?? "—")}
        />
      );
    case "risk":
      return <RiskScore score={Number(raw ?? 0)} />;
    case "risk_rating":
      return (
        <span>{RISK_RATING_LABEL[String(raw)] ?? titleCase(String(raw ?? "—"))}</span>
      );
    default:
      return <span>{raw == null || raw === "" ? "—" : String(raw)}</span>;
  }
}
