"use client";

import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { CaseRow, Column } from "@/lib/types";

function cell(row: CaseRow, column: Column): string {
  switch (column.type) {
    case "user":
      return row.assignee?.name ?? "";
    case "tag":
      return String(
        row.extra?.[`${column.key}_label`] ?? row.extra?.[column.key] ?? "",
      );
    default: {
      const raw =
        column.key in row
          ? row[column.key as keyof CaseRow]
          : row.extra?.[column.key];
      return raw == null ? "" : String(raw);
    }
  }
}

/** Works for any queue: columns come from the case type declaration. */
export function ExportCsvButton({
  rows,
  columns,
  filename,
}: {
  rows: CaseRow[];
  columns: Column[];
  filename: string;
}) {
  function download() {
    const lines = [
      columns.map((column) => column.label).join(","),
      ...rows.map((row) =>
        columns
          .map((column) => `"${cell(row, column).replace(/"/g, '""')}"`)
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
  }

  return (
    <Button variant="outline" size="sm" onClick={download}>
      <Download className="size-3.5" />
      Export CSV
    </Button>
  );
}
