import { cn } from "cn";

import type { BreakdownItem } from "@/lib/types";

import { TONE_DOT, asTone } from "./tone";

export function BreakdownBars({ items }: { items: BreakdownItem[] }) {
  const max = Math.max(1, ...items.map((item) => item.value));
  return (
    <div className="flex flex-col gap-2">
      {items.map((item) => (
        <div key={item.key} className="grid grid-cols-[1fr_2.5rem] items-center gap-3">
          <div className="min-w-0">
            <p className="mb-1 truncate text-xs text-muted-foreground">
              {item.label}
            </p>
            <div className="h-1.5 overflow-hidden rounded-full bg-muted">
              <div
                className={cn("h-full rounded-full", TONE_DOT[asTone(item.tone)])}
                style={{ width: `${(item.value / max) * 100}%` }}
              />
            </div>
          </div>
          <span className="text-right text-sm tabular-nums">{item.value}</span>
        </div>
      ))}
    </div>
  );
}
