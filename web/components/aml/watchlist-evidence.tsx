import { ShieldCheck } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { EvidenceProps } from "@/components/kit/evidence-tabs";
import { dateTime, titleCase } from "@/lib/format";

export function WatchlistEvidence({ detail }: EvidenceProps) {
  if (detail.watchlist_hits.length === 0) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <ShieldCheck className="size-4 text-emerald-600" />
        No sanctions, PEP or adverse-media hits on the latest screening run.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {detail.watchlist_hits.map((hit) => (
        <Card key={hit.id} className="gap-2 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="text-sm font-medium">{hit.matched_name}</p>
              <p className="text-xs text-muted-foreground">
                {hit.list_name} · screened {dateTime(hit.screened_at)}
              </p>
            </div>
            <Badge
              variant={hit.status === "confirmed" ? "destructive" : "secondary"}
            >
              {titleCase(hit.status)}
            </Badge>
          </div>
          <div className="flex items-center gap-3">
            <Progress value={hit.match_score} className="h-1.5 w-40" />
            <span className="text-xs tabular-nums text-muted-foreground">
              {hit.match_score}% name match
            </span>
          </div>
          <p className="text-sm text-muted-foreground">{hit.details}</p>
        </Card>
      ))}
    </div>
  );
}
