import type { components } from "./api/schema";

type S = components["schemas"];

export type User = S["UserOut"];
export type CaseType = S["CaseTypeOut"];
export type CaseRow = S["CaseRowOut"];
export type CaseList = S["CaseListOut"];
export type CaseDetail = S["CaseDetailOut"];
export type CaseEvent = S["CaseEventOut"];
export type Comment = S["CommentOut"];
export type Customer = S["CustomerOut"];
export type Account = S["AccountOut"];
export type Transaction = S["TransactionOut"];
export type WatchlistHit = S["WatchlistHitOut"];
export type RelatedCase = S["RelatedCaseOut"];
export type AvailableTransition = S["AvailableTransitionOut"];
export type Column = S["ColumnOut"];
export type Filter = S["FilterOut"];
export type Preset = S["PresetOut"];
export type SummaryField = S["SummaryFieldOut"];
export type EvidenceTab = S["EvidenceTabOut"];
export type State = S["StateOut"];
export type Metrics = S["MetricsOut"];
export type MetricTile = S["MetricTileOut"];
export type BreakdownItem = S["BreakdownItemOut"];
export type TrendPoint = S["TrendPointOut"];

export type Tone = "neutral" | "info" | "warn" | "danger" | "success";
