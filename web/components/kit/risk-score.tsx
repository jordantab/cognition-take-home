import { cn } from "cn";

import type { Tone } from "@/lib/types";

import { TONE_TEXT } from "./tone";

function toneFor(score: number): Tone {
  if (score >= 75) return "danger";
  if (score >= 55) return "warn";
  return "success";
}

export function RiskScore({
  score,
  showBar = true,
  className,
}: {
  score: number;
  showBar?: boolean;
  className?: string;
}) {
  const tone = toneFor(score);
  const bar = {
    danger: "bg-red-500",
    warn: "bg-amber-500",
    success: "bg-emerald-500",
    info: "bg-sky-500",
    neutral: "bg-slate-400",
  }[tone];

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <span className={cn("font-mono text-sm font-medium", TONE_TEXT[tone])}>
        {score}
      </span>
      {showBar ? (
        <span className="h-1.5 w-10 overflow-hidden rounded-full bg-muted">
          <span
            className={cn("block h-full rounded-full", bar)}
            style={{ width: `${Math.min(score, 100)}%` }}
          />
        </span>
      ) : null}
    </div>
  );
}
