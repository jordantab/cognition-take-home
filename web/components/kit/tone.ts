import type { Tone } from "@/lib/types";

/** Single source of truth for semantic colour across every block. */
export const TONE_BADGE: Record<Tone, string> = {
  neutral: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200",
  info: "bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-200",
  warn: "bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-200",
  danger: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200",
  success:
    "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200",
};

export const TONE_TEXT: Record<Tone, string> = {
  neutral: "text-slate-600 dark:text-slate-300",
  info: "text-sky-700 dark:text-sky-300",
  warn: "text-amber-700 dark:text-amber-300",
  danger: "text-red-700 dark:text-red-300",
  success: "text-emerald-700 dark:text-emerald-300",
};

export const TONE_DOT: Record<Tone, string> = {
  neutral: "bg-slate-400",
  info: "bg-sky-500",
  warn: "bg-amber-500",
  danger: "bg-red-500",
  success: "bg-emerald-500",
};

/**
 * Categorical palette for `tag` columns, whose values are dimensions (a
 * typology, a document type, a refund reason) rather than good/bad signals.
 * A case type maps its values onto these keys in its column declaration.
 */
export const TAG_PALETTE: Record<string, string> = {
  slate: "border-slate-200 bg-slate-50 text-slate-700",
  sky: "border-sky-200 bg-sky-50 text-sky-700",
  violet: "border-violet-200 bg-violet-50 text-violet-700",
  teal: "border-teal-200 bg-teal-50 text-teal-700",
  amber: "border-amber-200 bg-amber-50 text-amber-800",
  rose: "border-rose-200 bg-rose-50 text-rose-700",
  indigo: "border-indigo-200 bg-indigo-50 text-indigo-700",
};

export function asTone(value: string | null | undefined): Tone {
  return value && value in TONE_BADGE ? (value as Tone) : "neutral";
}
