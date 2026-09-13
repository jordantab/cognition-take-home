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
  slate: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200",
  sky: "bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-200",
  violet: "bg-violet-100 text-violet-800 dark:bg-violet-950 dark:text-violet-200",
  teal: "bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-200",
  amber: "bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-200",
  rose: "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-200",
  indigo: "bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-200",
};

export const TAG_PALETTE_DOT: Record<string, string> = {
  slate: "bg-slate-400",
  sky: "bg-sky-500",
  violet: "bg-violet-500",
  teal: "bg-teal-500",
  amber: "bg-amber-500",
  rose: "bg-rose-500",
  indigo: "bg-indigo-500",
};

export function asTone(value: string | null | undefined): Tone {
  return value && value in TONE_BADGE ? (value as Tone) : "neutral";
}
