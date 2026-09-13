import { cn } from "cn";

import { Badge } from "@/components/ui/badge";
import type { State } from "@/lib/types";
import { titleCase } from "@/lib/format";

import { TAG_PALETTE, TAG_PALETTE_DOT, TONE_BADGE, TONE_DOT, asTone } from "./tone";

/**
 * Renders any workflow state from the case type's declaration - the app never
 * hard-codes a status list.
 */
export function StatusBadge({
  status,
  states,
  className,
}: {
  status: string;
  states: State[];
  className?: string;
}) {
  const state = states.find((candidate) => candidate.key === status);
  const tone = asTone(state?.tone);
  return (
    <Badge
      variant="secondary"
      className={cn("gap-1.5 px-2", TONE_BADGE[tone], className)}
      title={state?.description}
    >
      <span className={cn("size-1.5 rounded-full", TONE_DOT[tone])} />
      {state?.label ?? titleCase(status)}
    </Badge>
  );
}

const PRIORITY_TONE = { high: "danger", medium: "warn", low: "neutral" } as const;

export function PriorityBadge({ priority }: { priority: string }) {
  const tone = asTone(
    PRIORITY_TONE[priority as keyof typeof PRIORITY_TONE] ?? "neutral",
  );
  return (
    <Badge variant="secondary" className={cn("px-2", TONE_BADGE[tone])}>
      {titleCase(priority)}
    </Badge>
  );
}

/** Categorical tag, styled like `StatusBadge` so the queue reads consistently. */
export function TagBadge({ label, color }: { label: string; color?: string }) {
  const swatch = color && color in TAG_PALETTE ? color : null;
  return (
    <Badge
      variant="secondary"
      className={cn(
        "max-w-full gap-1.5 px-2 font-normal",
        swatch ? TAG_PALETTE[swatch] : undefined,
      )}
    >
      {swatch ? (
        <span
          className={cn("size-1.5 shrink-0 rounded-full", TAG_PALETTE_DOT[swatch])}
        />
      ) : null}
      <span className="truncate">{label}</span>
    </Badge>
  );
}
