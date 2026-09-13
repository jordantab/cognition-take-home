"use client";

import { useRouter } from "next/navigation";
import { ArrowDown, ArrowUp, ChevronsUpDown } from "lucide-react";
import { cn } from "cn";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import type { CaseRow, Column, State } from "@/lib/types";
import { day, money } from "@/lib/format";

import { EmptyState } from "./empty-state";
import { PriorityBadge, StatusBadge, TagBadge } from "./status-badge";
import { RiskScore } from "./risk-score";
import { SlaClock } from "./sla-clock";
import { UserChip } from "./user-chip";
import { useQueueParams } from "./use-queue-params";

/**
 * Renders any case type's queue from its column declaration. Adding a new
 * internal app means shipping columns from the API, not writing a table.
 */
export function WorkQueue({
  rows,
  columns,
  states,
  basePath,
  total,
  page,
  pageSize,
}: {
  rows: CaseRow[];
  columns: Column[];
  states: State[];
  basePath: string;
  total: number;
  page: number;
  pageSize: number;
}) {
  const router = useRouter();
  const { params, setParams } = useQueueParams();
  const sort = params.get("sort") ?? "due_at";
  const direction = params.get("direction") ?? "asc";

  function toggleSort(key: string) {
    setParams({
      sort: key,
      direction: sort === key && direction === "asc" ? "desc" : "asc",
      page: "1",
    });
  }

  if (rows.length === 0) {
    return (
      <EmptyState
        title="Nothing in this view"
        description="Clear a filter or pick another saved view to see more work."
      />
    );
  }

  const lastPage = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="flex flex-col">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              {columns.map((column) => (
                <TableHead
                  key={column.key}
                  style={column.width ? { width: column.width } : undefined}
                  className="whitespace-nowrap"
                >
                  {column.sortable ? (
                    <button
                      type="button"
                      onClick={() => toggleSort(column.key)}
                      className="inline-flex items-center gap-1 hover:text-foreground"
                    >
                      {column.label}
                      {sort !== column.key ? (
                        <ChevronsUpDown className="size-3 opacity-40" />
                      ) : direction === "asc" ? (
                        <ArrowUp className="size-3" />
                      ) : (
                        <ArrowDown className="size-3" />
                      )}
                    </button>
                  ) : (
                    column.label
                  )}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow
                key={row.id}
                onClick={() => router.push(`${basePath}/${row.id}`)}
                className={cn(
                  "cursor-pointer",
                  row.overdue && !row.closed_at && "bg-red-50/40 dark:bg-red-950/10",
                )}
              >
                {columns.map((column) => (
                  <TableCell key={column.key} className="align-middle">
                    <Cell row={row} column={column} states={states} />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between border-t px-4 py-3 text-sm text-muted-foreground">
        <span>
          {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} of{" "}
          {total}
        </span>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setParams({ page: String(page - 1) })}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= lastPage}
            onClick={() => setParams({ page: String(page + 1) })}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}

function value(row: CaseRow, key: string): unknown {
  if (key in row) return row[key as keyof CaseRow];
  return row.extra?.[key];
}

function Cell({
  row,
  column,
  states,
}: {
  row: CaseRow;
  column: Column;
  states: State[];
}) {
  const raw = value(row, column.key);

  switch (column.type) {
    case "reference":
      return (
        <span className="font-mono text-xs font-medium">{row.reference}</span>
      );
    case "status":
      return <StatusBadge status={row.status} states={states} />;
    case "priority":
      return <PriorityBadge priority={row.priority} />;
    case "risk":
      return <RiskScore score={row.risk_score} />;
    case "money":
      return (
        <span className="tabular-nums">{money(Number(raw ?? 0))}</span>
      );
    case "user":
      return <UserChip user={row.assignee} />;
    case "sla":
      return (
        <SlaClock
          hoursRemaining={row.hours_remaining}
          overdue={row.overdue}
          closed={Boolean(row.closed_at)}
        />
      );
    case "tag":
      return (
        <TagBadge
          label={String(row.extra?.[`${column.key}_label`] ?? raw ?? "—")}
        />
      );
    case "date":
      return (
        <span className="text-sm text-muted-foreground">
          {raw ? day(String(raw)) : "—"}
        </span>
      );
    default:
      return (
        <span className="block max-w-[28rem] truncate text-sm">
          {raw == null || raw === "" ? "—" : String(raw)}
        </span>
      );
  }
}
