import "server-only";

import { readFile } from "node:fs/promises";
import path from "node:path";

export type Block = {
  name: string;
  file: string;
  layer: "ui" | "platform" | "app";
  description: string;
};

/** The reusable kit, plus the app-specific pieces, for the gallery page. */
export const BLOCKS: Block[] = [
  {
    name: "AppShell",
    file: "components/kit/app-shell.tsx",
    layer: "platform",
    description:
      "Navigation generated from the registered case types, plus mock identity.",
  },
  {
    name: "PersonaSwitcher",
    file: "components/kit/persona-switcher.tsx",
    layer: "platform",
    description: "Switch user to see role-based permissions change live.",
  },
  {
    name: "WorkQueue",
    file: "components/kit/work-queue.tsx",
    layer: "platform",
    description:
      "Sortable, paginated queue rendered from a case type's column declaration.",
  },
  {
    name: "FilterBar",
    file: "components/kit/filter-bar.tsx",
    layer: "platform",
    description: "Saved views and filters, also declared server-side.",
  },
  {
    name: "MetricTiles",
    file: "components/kit/metric-tiles.tsx",
    layer: "platform",
    description: "KPI row driven by the generic metrics endpoint.",
  },
  {
    name: "TrendChart",
    file: "components/kit/trend-chart.tsx",
    layer: "platform",
    description: "Opened vs closed volume over time.",
  },
  {
    name: "BreakdownBars",
    file: "components/kit/breakdown-bars.tsx",
    layer: "platform",
    description: "Any categorical breakdown the API returns.",
  },
  {
    name: "CaseShell",
    file: "components/kit/case-shell.tsx",
    layer: "platform",
    description: "Two-column case workspace with header, SLA and risk.",
  },
  {
    name: "DecisionPanel",
    file: "components/kit/decision-panel.tsx",
    layer: "platform",
    description:
      "Workflow actions with required notes, reason codes and four-eyes locks.",
  },
  {
    name: "AuditTimeline",
    file: "components/kit/audit-timeline.tsx",
    layer: "platform",
    description: "Append-only history of every state change and note.",
  },
  {
    name: "CommentThread",
    file: "components/kit/comment-thread.tsx",
    layer: "platform",
    description: "Case discussion, gated on the comment permission.",
  },
  {
    name: "AssigneePicker",
    file: "components/kit/assignee-picker.tsx",
    layer: "platform",
    description: "Ownership changes, audited like any other event.",
  },
  {
    name: "EvidenceTabs",
    file: "components/kit/evidence-tabs.tsx",
    layer: "platform",
    description:
      "The seam where an app plugs its own evidence components into the shell.",
  },
  {
    name: "SummaryList",
    file: "components/kit/summary-list.tsx",
    layer: "platform",
    description: "Key facts rendered from declared summary fields.",
  },
  {
    name: "StatusBadge",
    file: "components/kit/status-badge.tsx",
    layer: "platform",
    description: "Status, priority and tag badges with shared semantic tones.",
  },
  {
    name: "SlaClock",
    file: "components/kit/sla-clock.tsx",
    layer: "platform",
    description: "Countdown and breach state against the case type's SLA.",
  },
  {
    name: "RoleGate",
    file: "components/kit/role-gate.tsx",
    layer: "platform",
    description: "Hide or replace UI the current role cannot use.",
  },
  {
    name: "ExportCsvButton",
    file: "components/kit/export-csv-button.tsx",
    layer: "platform",
    description: "CSV export of any queue, from the same column declaration.",
  },
  {
    name: "TransactionEvidence",
    file: "components/aml/transaction-evidence.tsx",
    layer: "app",
    description: "AML-specific: flagged transactions in context.",
  },
  {
    name: "CustomerEvidence",
    file: "components/aml/customer-evidence.tsx",
    layer: "app",
    description: "AML-specific: customer profile and accounts.",
  },
  {
    name: "WatchlistEvidence",
    file: "components/aml/watchlist-evidence.tsx",
    layer: "app",
    description: "AML-specific: sanctions and PEP screening hits.",
  },
  {
    name: "RelatedCasesEvidence",
    file: "components/aml/related-cases-evidence.tsx",
    layer: "app",
    description: "AML-specific: other alerts on the same customer.",
  },
];

export type BlockWithSize = Block & { lines: number };

async function lineCount(relative: string): Promise<number> {
  try {
    const contents = await readFile(
      path.join(/* turbopackIgnore: true */ process.cwd(), relative),
      "utf8",
    );
    return contents.trimEnd().split("\n").length;
  } catch {
    return 0;
  }
}

export async function blocksWithSizes(): Promise<BlockWithSize[]> {
  return Promise.all(
    BLOCKS.map(async (block) => ({
      ...block,
      lines: await lineCount(block.file),
    })),
  );
}

/** The AML case type declaration - the "config, not code" exhibit. */
export async function caseTypeSource(key: string): Promise<string> {
  try {
    return await readFile(
      path.join(
        /* turbopackIgnore: true */ process.cwd(),
        "..",
        "api",
        "app",
        "casetypes",
        `${key}.py`,
      ),
      "utf8",
    );
  } catch {
    return "";
  }
}
