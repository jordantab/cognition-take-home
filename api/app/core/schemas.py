from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    role_label: str
    job_title: str
    team: str
    initials: str
    permissions: list[str]


class StateOut(BaseModel):
    key: str
    label: str
    tone: str
    terminal: bool
    description: str


class ReasonCodeOut(BaseModel):
    key: str
    label: str


class TransitionOut(BaseModel):
    key: str
    label: str
    to_state: str
    variant: str
    requires_note: bool
    requires_reason_code: bool
    reason_codes: list[ReasonCodeOut]
    description: str


class AvailableTransitionOut(TransitionOut):
    enabled: bool
    disabled_reason: str | None = None


class ColumnOut(BaseModel):
    key: str
    label: str
    type: str
    sortable: bool
    width: str | None
    primary: bool
    tones: dict[str, str] = {}


class FilterOptionOut(BaseModel):
    value: str
    label: str


class FilterOut(BaseModel):
    key: str
    label: str
    type: str
    options: list[FilterOptionOut]
    placeholder: str


class SummaryFieldOut(BaseModel):
    key: str
    label: str
    type: str
    tones: dict[str, str] = {}


class EvidenceTabOut(BaseModel):
    key: str
    label: str
    component: str


class PresetOut(BaseModel):
    key: str
    label: str
    filters: dict[str, str]
    mine: bool
    default: bool = False
    default_for_roles: list[str] = []


class CaseTypeOut(BaseModel):
    key: str
    label: str
    plural_label: str
    description: str
    icon: str
    reference_prefix: str
    sla_hours: int
    states: list[StateOut]
    transitions: list[TransitionOut]
    columns: list[ColumnOut]
    filters: list[FilterOut]
    summary_fields: list[SummaryFieldOut]
    evidence_tabs: list[EvidenceTabOut]
    presets: list[PresetOut]


class CaseRowOut(BaseModel):
    id: str
    case_type: str
    reference: str
    title: str
    status: str
    priority: str
    risk_score: int
    amount: float
    currency: str
    subject_id: str | None
    subject_name: str | None
    assignee: UserOut | None
    opened_at: datetime
    due_at: datetime
    closed_at: datetime | None
    overdue: bool
    hours_remaining: float
    extra: dict[str, Any]


class CaseListOut(BaseModel):
    items: list[CaseRowOut]
    total: int
    page: int
    page_size: int
    status_counts: dict[str, int]


class CustomerOut(BaseModel):
    id: str
    name: str
    kind: str
    country: str
    segment: str
    risk_rating: str
    kyc_status: str
    is_pep: bool
    occupation: str
    email: str
    onboarded_at: datetime
    lifetime_volume: float


class AccountOut(BaseModel):
    id: str
    number: str
    kind: str
    currency: str
    balance: float
    status: str
    opened_at: datetime


class TransactionOut(BaseModel):
    id: str
    account_id: str
    posted_at: datetime
    amount: float
    currency: str
    direction: str
    channel: str
    counterparty_name: str
    counterparty_country: str
    description: str
    is_flagged: bool


class WatchlistHitOut(BaseModel):
    id: str
    list_name: str
    matched_name: str
    match_score: int
    status: str
    details: str
    screened_at: datetime


class CaseEventOut(BaseModel):
    id: str
    kind: str
    actor: UserOut | None
    transition_key: str | None
    transition_label: str | None
    from_status: str | None
    to_status: str | None
    reason_code: str | None
    reason_label: str | None
    note: str | None
    created_at: datetime
    meta: dict[str, Any]


class CommentOut(BaseModel):
    id: str
    author: UserOut
    body: str
    created_at: datetime


class RelatedCaseOut(BaseModel):
    id: str
    reference: str
    title: str
    status: str
    opened_at: datetime
    risk_score: int


class CaseDetailOut(BaseModel):
    case: CaseRowOut
    subject: CustomerOut | None
    accounts: list[AccountOut]
    transactions: list[TransactionOut]
    watchlist_hits: list[WatchlistHitOut]
    related_cases: list[RelatedCaseOut]
    events: list[CaseEventOut]
    comments: list[CommentOut]
    available_transitions: list[AvailableTransitionOut]
    can_comment: bool
    can_assign_others: bool
    can_claim: bool


class TransitionRequest(BaseModel):
    transition: str
    note: str | None = None
    reason_code: str | None = None


class CommentRequest(BaseModel):
    body: str


class AssignRequest(BaseModel):
    assignee_id: str | None = None


class MetricTileOut(BaseModel):
    key: str
    label: str
    value: float
    format: str  # number|money|hours|percent
    hint: str | None = None
    tone: str = "neutral"


class BreakdownItemOut(BaseModel):
    key: str
    label: str
    value: int
    tone: str = "neutral"


class TrendPointOut(BaseModel):
    date: str
    opened: int
    closed: int


class MetricsOut(BaseModel):
    tiles: list[MetricTileOut]
    by_status: list[BreakdownItemOut]
    by_typology: list[BreakdownItemOut]
    trend: list[TrendPointOut]
