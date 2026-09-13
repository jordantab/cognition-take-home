import { cn } from "cn";

import { Card } from "@/components/ui/card";
import type { MetricTile } from "@/lib/types";
import { metricValue } from "@/lib/format";

import { TONE_TEXT, asTone } from "./tone";

export function MetricTiles({ tiles }: { tiles: MetricTile[] }) {
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
      {tiles.map((tile) => (
        <Card key={tile.key} className="gap-1 p-4">
          <p className="text-xs font-medium text-muted-foreground">
            {tile.label}
          </p>
          <p
            className={cn(
              "text-2xl font-semibold tabular-nums",
              TONE_TEXT[asTone(tile.tone)],
            )}
          >
            {metricValue(tile.value, tile.format)}
          </p>
          {tile.hint ? (
            <p className="text-xs text-muted-foreground">{tile.hint}</p>
          ) : null}
        </Card>
      ))}
    </div>
  );
}
