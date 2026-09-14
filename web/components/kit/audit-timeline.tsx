import { cn } from "cn";
import {
  ArrowRightLeft,
  MessageSquare,
  Sparkles,
  UserCog,
} from "lucide-react";

import type { CaseEvent, State } from "@/lib/types";
import { dateTime, relative } from "@/lib/format";

import { StatusBadge } from "./status-badge";

const ICONS = {
  transition: ArrowRightLeft,
  comment: MessageSquare,
  assignment: UserCog,
  created: Sparkles,
} as const;

/** Append-only history, identical for every case type. */
export function AuditTimeline({
  events,
  states,
}: {
  events: CaseEvent[];
  states: State[];
}) {
  const ordered = [...events].reverse();
  return (
    <ol className="flex flex-col">
      {ordered.map((event, index) => {
        const Icon = ICONS[event.kind as keyof typeof ICONS] ?? Sparkles;
        return (
          <li key={event.id} className="flex gap-3">
            <div className="flex flex-col items-center">
              <span className="flex size-7 items-center justify-center rounded-full border bg-background">
                <Icon className="size-3.5 text-muted-foreground" />
              </span>
              <span
                className={cn(
                  "w-px flex-1 bg-border",
                  index === ordered.length - 1 && "bg-transparent",
                )}
              />
            </div>
            <div className="min-w-0 pb-5">
              <p className="text-sm">
                <span className="font-medium">
                  {event.actor?.name ?? "System"}
                </span>{" "}
                <span className="text-muted-foreground">
                  {describe(event)}
                </span>
              </p>
              {event.to_status ? (
                <div className="mt-1.5 flex items-center gap-1.5">
                  <StatusBadge status={event.to_status} states={states} />
                  {event.reason_label ? (
                    <span className="text-xs text-muted-foreground">
                      {event.reason_label}
                    </span>
                  ) : null}
                </div>
              ) : null}
              {event.note ? (
                <p className="mt-1.5 border-l-2 pl-3 text-sm text-muted-foreground">
                  {event.note}
                </p>
              ) : null}
              <p
                className="mt-1 text-xs text-muted-foreground"
                title={dateTime(event.created_at)}
              >
                {relative(event.created_at)}
              </p>
            </div>
          </li>
        );
      })}
    </ol>
  );
}

function describe(event: CaseEvent): string {
  switch (event.kind) {
    case "transition":
      return event.transition_label
        ? `applied "${event.transition_label}"`
        : "changed the status";
    case "comment":
      return "commented";
    case "assignment":
      return "changed the owner";
    default:
      return "updated the case";
  }
}
