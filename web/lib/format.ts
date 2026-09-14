const MONEY = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const MONEY_EXACT = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
});

export function money(value: number, exact = false): string {
  return exact ? MONEY_EXACT.format(value) : MONEY.format(value);
}

export function compactMoney(value: number): string {
  if (Math.abs(value) >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (Math.abs(value) >= 1_000) return `$${Math.round(value / 1_000)}k`;
  return money(value);
}

export function dateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZone: "UTC",
  });
}

export function day(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
}

export function relative(iso: string, from: Date = new Date()): string {
  const diffMs = new Date(iso).getTime() - from.getTime();
  const minutes = Math.round(diffMs / 60_000);
  const abs = Math.abs(minutes);
  const rtf = new Intl.RelativeTimeFormat("en-US", { numeric: "auto" });
  if (abs < 60) return rtf.format(minutes, "minute");
  if (abs < 60 * 24) return rtf.format(Math.round(minutes / 60), "hour");
  return rtf.format(Math.round(minutes / (60 * 24)), "day");
}

export function duration(hours: number): string {
  const abs = Math.abs(hours);
  if (abs < 1) return `${Math.round(abs * 60)}m`;
  if (abs < 48) return `${Math.round(abs)}h`;
  return `${Math.round(abs / 24)}d`;
}

export function metricValue(value: number, format: string): string {
  switch (format) {
    case "money":
      return compactMoney(value);
    case "percent":
      return `${value}%`;
    case "hours":
      return duration(value);
    default:
      return new Intl.NumberFormat("en-US").format(value);
  }
}

export function titleCase(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/^\w/, (character) => character.toUpperCase());
}
