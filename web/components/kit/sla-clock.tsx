import { cn } from "cn";
import { Clock, TriangleAlert } from "lucide-react";

import { duration } from "@/lib/format";

/** SLA countdown, driven by the hours the API already computed. */
export function SlaClock({
  hoursRemaining,
  overdue,
  closed = false,
  className,
}: {
  hoursRemaining: number;
  overdue: boolean;
  closed?: boolean;
  className?: string;
}) {
  if (closed) {
    return <span className={cn("text-xs text-muted-foreground", className)}>—</span>;
  }
  const soon = !overdue && hoursRemaining <= 12;
  const Icon = overdue ? TriangleAlert : Clock;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-xs font-medium tabular-nums",
        overdue
          ? "text-red-600 dark:text-red-400"
          : soon
            ? "text-amber-600 dark:text-amber-400"
            : "text-muted-foreground",
        className,
      )}
    >
      <Icon className="size-3.5" />
      {overdue
        ? `${duration(hoursRemaining)} over`
        : `${duration(hoursRemaining)} left`}
    </span>
  );
}
