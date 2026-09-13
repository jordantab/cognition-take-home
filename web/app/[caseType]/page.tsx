import { notFound } from "next/navigation";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BreakdownBars } from "@/components/kit/breakdown-bars";
import { ExportCsvButton } from "@/components/kit/export-csv-button";
import { FilterBar } from "@/components/kit/filter-bar";
import { MetricTiles } from "@/components/kit/metric-tiles";
import { PageHeader } from "@/components/kit/page-header";
import { TrendChart } from "@/components/kit/trend-chart";
import { WorkQueue } from "@/components/kit/work-queue";
import { can } from "@/components/kit/role-gate";
import {
  ApiError,
  getCaseType,
  getCases,
  getCurrentUser,
  getMetrics,
} from "@/lib/api";

const PAGE_SIZE = 15;

function pick(
  params: Record<string, string | string[] | undefined>,
  key: string,
): string | undefined {
  const value = params[key];
  return Array.isArray(value) ? value[0] : value;
}

export default async function QueuePage({
  params,
  searchParams,
}: PageProps<"/[caseType]">) {
  const { caseType } = await params;
  const query = await searchParams;

  const config = await getCaseType(caseType).catch((error) => {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  });

  const page = Number(pick(query, "page") ?? 1);
  const currentUser = await getCurrentUser();
  // `me` keeps "my work" views pinned to whoever is signed in, not to an id
  // captured when the view was clicked.
  const assignee = pick(query, "assignee_id");
  const filters = {
    status: pick(query, "status"),
    assignee_id: assignee === "me" ? currentUser.id : assignee,
    priority: pick(query, "priority"),
    typology: pick(query, "typology"),
    q: pick(query, "q"),
    open_only: pick(query, "open_only"),
    sort: pick(query, "sort") ?? "due_at",
    direction: pick(query, "direction") ?? "asc",
  };

  const [list, metrics] = await Promise.all([
    getCases(caseType, { ...filters, page, page_size: PAGE_SIZE }),
    getMetrics(caseType),
  ]);

  // Export every row matching the current filters, not just the page on screen.
  async function exportRows() {
    "use server";
    const all = await getCases(caseType, {
      ...filters,
      page: 1,
      page_size: 1000,
    });
    return all.items;
  }

  return (
    <div className="flex flex-col">
      <PageHeader
        title={config.plural_label}
        description={config.description}
        actions={
          can(currentUser, "case:export") ? (
            <ExportCsvButton
              columns={config.columns}
              states={config.states}
              total={list.total}
              fetchRows={exportRows}
              filename={`${config.key}-queue.csv`}
            />
          ) : null
        }
      />

      <div className="space-y-6 p-6">
        <MetricTiles tiles={metrics.tiles} />

        <div className="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">
                Opened vs closed, last 14 days
              </CardTitle>
            </CardHeader>
            <CardContent>
              <TrendChart data={metrics.trend} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">By typology</CardTitle>
            </CardHeader>
            <CardContent>
              <BreakdownBars items={metrics.by_typology} />
            </CardContent>
          </Card>
        </div>

        <Card className="gap-0 py-0">
          <div className="border-b p-4">
            <FilterBar
              filters={config.filters}
              presets={config.presets}
              currentUserId={currentUser.id}
            />
          </div>
          <WorkQueue
            rows={list.items}
            columns={config.columns}
            states={config.states}
            basePath={`/${caseType}`}
            total={list.total}
            page={list.page}
            pageSize={list.page_size}
          />
        </Card>
      </div>
    </div>
  );
}
