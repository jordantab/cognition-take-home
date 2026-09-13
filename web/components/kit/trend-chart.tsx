"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { TrendPoint } from "@/lib/types";

// The theme's chart tokens are near-monochrome, which makes a two-series
// legend useless, so the intake/outflow pair gets its own hues.
const OPENED = "var(--color-sky-500)";
const CLOSED = "var(--color-emerald-500)";

export function TrendChart({ data }: { data: TrendPoint[] }) {
  const points = data.map((point) => ({
    ...point,
    label: new Date(`${point.date}T00:00:00Z`).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      timeZone: "UTC",
    }),
  }));

  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={points} margin={{ left: -16, right: 8, top: 8 }}>
        <defs>
          <linearGradient id="opened" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={OPENED} stopOpacity={0.35} />
            <stop offset="100%" stopColor={OPENED} stopOpacity={0} />
          </linearGradient>
          <linearGradient id="closed" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={CLOSED} stopOpacity={0.35} />
            <stop offset="100%" stopColor={CLOSED} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} strokeDasharray="3 3" opacity={0.3} />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={false}
          fontSize={11}
          interval={2}
        />
        <YAxis
          allowDecimals={false}
          tickLine={false}
          axisLine={false}
          fontSize={11}
          width={40}
        />
        <Legend
          verticalAlign="top"
          align="right"
          height={24}
          iconType="plainline"
          iconSize={12}
          formatter={(value) => (
            <span className="text-xs text-muted-foreground">{value}</span>
          )}
        />
        <Tooltip
          contentStyle={{
            borderRadius: 8,
            border: "1px solid var(--color-border)",
            background: "var(--color-popover)",
            fontSize: 12,
          }}
        />
        <Area
          type="monotone"
          dataKey="opened"
          name="Opened"
          stroke={OPENED}
          fill="url(#opened)"
          strokeWidth={2}
        />
        <Area
          type="monotone"
          dataKey="closed"
          name="Closed"
          stroke={CLOSED}
          fill="url(#closed)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
