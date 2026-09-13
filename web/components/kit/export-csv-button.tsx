"use client";

import { Download } from "lucide-react";
import { useTransition } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { dateTime, titleCase } from "@/lib/format";
import type { CaseRow, Column, State } from "@/lib/types";

function cell(row: CaseRow, column: Column, states: State[]): string {
  const raw =
    column.key in row
      ? row[column.key as keyof CaseRow]
      : row.extra?.[column.key];

  switch (column.type) {
    case "user":
      return row.assignee?.name ?? "Unassigned";
    case "status":
      return (
        states.find((state) => state.key === row.status)?.label ??
        titleCase(row.status)
      );
    case "priority":
      return titleCase(row.priority);
    case "tag":
      return String(
        row.extra?.[`${column.key}_label`] ?? row.extra?.[column.key] ?? "",
      );
    case "sla":
      return `${dateTime(row.due_at)}${row.overdue ? " (overdue)" : ""}`;
    case "date":
      return typeof raw === "string" ? dateTime(raw) : "";
    default:
      return raw == null ? "" : String(raw);
  }
}

/**
 * Works for any queue: columns come from the case type declaration, and the
 * export covers every row matching the current filters, not just this page.
 */
export function ExportCsvButton({
  columns,
  states,
  filename,
  total,
  fetchRows,
}: {
  columns: Column[];
  states: State[];
  filename: string;
  total: number;
  fetchRows: () => Promise<CaseRow[]>;
}) {
  const [pending, startTransition] = useTransition();

  function download() {
    startTransition(async () => {
      const rows = await fetchRows();
      const lines = [
        columns.map((column) => column.label).join(","),
        ...rows.map((row) =>
          columns
            .map(
              (column) => `"${cell(row, column, states).replace(/"/g, '""')}"`,
            )
            .join(","),
        ),
      ];
      const url = URL.createObjectURL(
        new Blob([lines.join("\n")], { type: "text/csv" }),
      );
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
      toast.success(`Exported ${rows.length} rows`);
    });
  }

  return (
    <Button variant="outline" size="sm" onClick={download} disabled={pending}>
      <Download className="size-3.5" />
      {pending ? "Exporting..." : `Export CSV (${total})`}
    </Button>
  );
}
