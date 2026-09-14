"""Generic case service: querying, decisioning, audit and metrics.

Nothing here knows what an AML alert is. It reads the case type's declaration
and enforces it.
"""

from __future__ import annotations

import uuid
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.identity import to_user_out
from app.core.models import (
    Account,
    Case,
    CaseEvent,
    Comment,
    Customer,
    Transaction,
    User,
    WatchlistHit,
)
from app.core.rbac import Permission, Role, has_permission
from app.core.schemas import (
    AccountOut,
    AvailableTransitionOut,
    BreakdownItemOut,
    CaseDetailOut,
    CaseEventOut,
    CaseListOut,
    CaseRowOut,
    CaseTypeOut,
    CommentOut,
    CustomerOut,
    FilterOptionOut,
    MetricsOut,
    MetricTileOut,
    RelatedCaseOut,
    TransactionOut,
    TrendPointOut,
    UserOut,
    WatchlistHitOut,
)
from app.core.workflow import CaseTypeConfig, Transition

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def as_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# --------------------------------------------------------------------------
# Case type declaration -> API payload
# --------------------------------------------------------------------------


def case_type_out(
    config: CaseTypeConfig, users: list[User], viewer: User
) -> CaseTypeOut:
    data: dict[str, Any] = asdict(config)
    role = Role(viewer.role)
    data["presets"] = [
        {k: v for k, v in p.items() if k != "requires_permission"}
        for p in data["presets"]
        if p["requires_permission"] is None
        or has_permission(role, p["requires_permission"])
    ]
    for f in data["filters"]:
        if f["key"] == "assignee_id":
            f["options"] = [{"value": u.id, "label": u.name} for u in users]
    for c in (*data["columns"], *data["summary_fields"]):
        c["tones"] = dict(c.get("tones") or ())
    for t in data["transitions"]:
        t.pop("from_states", None)
        t.pop("permission", None)
        t.pop("distinct_actor_from", None)
        t.pop("assigns_to_actor", None)
    return CaseTypeOut.model_validate(data)


def filter_options_for_users(users: list[User]) -> list[FilterOptionOut]:
    return [FilterOptionOut(value=u.id, label=u.name) for u in users]


# --------------------------------------------------------------------------
# Rows
# --------------------------------------------------------------------------


def row_out(
    case: Case,
    users: dict[str, User],
    customers: dict[str, Customer],
    reference_time: datetime | None = None,
) -> CaseRowOut:
    reference_time = reference_time or now()
    assignee = users.get(case.assignee_id) if case.assignee_id else None
    subject = customers.get(case.subject_id) if case.subject_id else None
    extra: dict[str, Any] = dict(case.payload)
    if subject:
        extra.setdefault("customer_risk_rating", subject.risk_rating)
        extra.setdefault("customer_country", subject.country)
    hours_remaining = (case.due_at - reference_time).total_seconds() / 3600
    return CaseRowOut(
        id=case.id,
        case_type=case.case_type,
        reference=case.reference,
        title=case.title,
        status=case.status,
        priority=case.priority,
        risk_score=case.risk_score,
        amount=case.amount,
        currency=case.currency,
        subject_id=case.subject_id,
        subject_name=subject.name if subject else None,
        assignee=to_user_out(assignee) if assignee else None,
        opened_at=as_utc(case.opened_at),
        due_at=as_utc(case.due_at),
        closed_at=as_utc(case.closed_at) if case.closed_at else None,
        overdue=case.closed_at is None and hours_remaining < 0,
        hours_remaining=round(hours_remaining, 1),
        extra=extra,
    )


def list_cases(
    session: Session,
    config: CaseTypeConfig,
    current_user: User,
    *,
    status_filter: str | None = None,
    assignee_id: str | None = None,
    priority: str | None = None,
    typology: str | None = None,
    query: str | None = None,
    open_only: bool = False,
    sort: str = "due_at",
    direction: str = "asc",
    page: int = 1,
    page_size: int = 25,
) -> CaseListOut:
    users = {u.id: u for u in session.exec(select(User)).all()}
    customers = {c.id: c for c in session.exec(select(Customer)).all()}
    cases = session.exec(select(Case).where(Case.case_type == config.key)).all()

    if status_filter:
        cases = [c for c in cases if c.status == status_filter]
    if open_only:
        open_states = set(config.open_states())
        cases = [c for c in cases if c.status in open_states]
    if assignee_id == "unassigned":
        cases = [c for c in cases if c.assignee_id is None]
    elif assignee_id:
        cases = [c for c in cases if c.assignee_id == assignee_id]
    if priority:
        cases = [c for c in cases if c.priority == priority]
    if typology:
        cases = [c for c in cases if c.payload.get("typology") == typology]
    if query:
        needle = query.lower().strip()

        def matches(case: Case) -> bool:
            subject = customers.get(case.subject_id) if case.subject_id else None
            haystack = " ".join(
                [
                    case.reference,
                    case.title,
                    subject.name if subject else "",
                    str(case.payload.get("rule_name", "")),
                    str(case.payload.get("typology_label", "")),
                ]
            ).lower()
            return needle in haystack

        cases = [c for c in cases if matches(c)]

    status_counts = Counter(c.status for c in cases)
    reference_time = now()
    rows = [row_out(c, users, customers, reference_time) for c in cases]

    def sort_key(row: CaseRowOut) -> Any:
        if sort == "priority":
            return (PRIORITY_ORDER.get(row.priority, 9), row.due_at)
        if sort == "subject_name":
            return (row.subject_name or "").lower()
        value = getattr(row, sort, None)
        if value is None:
            value = row.extra.get(sort)
        if value is None:
            return ""
        return value

    rows.sort(key=sort_key, reverse=direction == "desc")

    total = len(rows)
    start = max(page - 1, 0) * page_size
    return CaseListOut(
        items=rows[start : start + page_size],
        total=total,
        page=page,
        page_size=page_size,
        status_counts=dict(status_counts),
    )


# --------------------------------------------------------------------------
# Detail + decisioning
# --------------------------------------------------------------------------


def _transition_blocked_reason(
    config: CaseTypeConfig,
    transition: Transition,
    case: Case,
    user: User,
    events: list[CaseEvent],
) -> str | None:
    if case.status not in transition.from_states:
        return "Not available from the current status."
    if not has_permission(Role(user.role), transition.permission):
        return f"Requires the {transition.permission} permission."
    if transition.distinct_actor_from:
        prior = next(
            (
                e
                for e in sorted(events, key=lambda e: e.created_at, reverse=True)
                if e.transition_key == transition.distinct_actor_from
            ),
            None,
        )
        if prior and prior.actor_id == user.id:
            return "Four-eyes control: the approver must differ from the recommending analyst."
    return None


def available_transitions(
    config: CaseTypeConfig,
    case: Case,
    user: User,
    events: list[CaseEvent],
) -> list[AvailableTransitionOut]:
    out: list[AvailableTransitionOut] = []
    for transition in config.transitions:
        if case.status not in transition.from_states:
            continue
        reason = _transition_blocked_reason(config, transition, case, user, events)
        out.append(
            AvailableTransitionOut(
                key=transition.key,
                label=transition.label,
                to_state=transition.to_state,
                variant=transition.variant,
                requires_note=transition.requires_note,
                requires_reason_code=transition.requires_reason_code,
                reason_codes=[
                    {"key": r.key, "label": r.label} for r in transition.reason_codes
                ],
                description=transition.description,
                enabled=reason is None,
                disabled_reason=reason,
            )
        )
    return out


def _event_out(
    event: CaseEvent,
    users: dict[str, User],
    config: CaseTypeConfig,
) -> CaseEventOut:
    transition = (
        config.transition(event.transition_key) if event.transition_key else None
    )
    reason_label = None
    if transition and event.reason_code:
        reason_label = next(
            (r.label for r in transition.reason_codes if r.key == event.reason_code),
            event.reason_code,
        )
    actor = users.get(event.actor_id) if event.actor_id else None
    return CaseEventOut(
        id=event.id,
        kind=event.kind,
        actor=to_user_out(actor) if actor else None,
        transition_key=event.transition_key,
        transition_label=transition.label if transition else None,
        from_status=event.from_status,
        to_status=event.to_status,
        reason_code=event.reason_code,
        reason_label=reason_label,
        note=event.note,
        created_at=as_utc(event.created_at),
        meta=event.meta or {},
    )


def get_case_detail(
    session: Session,
    config: CaseTypeConfig,
    case: Case,
    current_user: User,
) -> CaseDetailOut:
    users = {u.id: u for u in session.exec(select(User)).all()}
    customers = {c.id: c for c in session.exec(select(Customer)).all()}
    subject = customers.get(case.subject_id) if case.subject_id else None

    accounts: list[Account] = []
    transactions: list[Transaction] = []
    hits: list[WatchlistHit] = []
    related: list[Case] = []
    if subject:
        accounts = list(
            session.exec(select(Account).where(Account.customer_id == subject.id)).all()
        )
        flagged_ids = set(case.payload.get("transaction_ids", []))
        customer_txns = session.exec(
            select(Transaction).where(Transaction.customer_id == subject.id)
        ).all()
        customer_txns = sorted(customer_txns, key=lambda t: t.posted_at, reverse=True)
        transactions = [t for t in customer_txns if t.id in flagged_ids] + [
            t for t in customer_txns if t.id not in flagged_ids
        ][:40]
        hits = list(
            session.exec(
                select(WatchlistHit).where(WatchlistHit.customer_id == subject.id)
            ).all()
        )
        related = [
            c
            for c in session.exec(
                select(Case).where(Case.subject_id == subject.id)
            ).all()
            if c.id != case.id
        ]

    events = list(
        session.exec(select(CaseEvent).where(CaseEvent.case_id == case.id)).all()
    )
    events.sort(key=lambda e: e.created_at)
    comments = list(
        session.exec(select(Comment).where(Comment.case_id == case.id)).all()
    )
    comments.sort(key=lambda c: c.created_at)

    return CaseDetailOut(
        case=row_out(case, users, customers),
        subject=CustomerOut.model_validate(subject, from_attributes=True)
        if subject
        else None,
        accounts=[AccountOut.model_validate(a, from_attributes=True) for a in accounts],
        transactions=[
            TransactionOut.model_validate(t, from_attributes=True) for t in transactions
        ],
        watchlist_hits=[
            WatchlistHitOut.model_validate(h, from_attributes=True) for h in hits
        ],
        related_cases=[
            RelatedCaseOut(
                id=c.id,
                reference=c.reference,
                title=c.title,
                status=c.status,
                opened_at=as_utc(c.opened_at),
                risk_score=c.risk_score,
            )
            for c in sorted(related, key=lambda c: c.opened_at, reverse=True)
        ],
        events=[_event_out(e, users, config) for e in events],
        comments=[
            CommentOut(
                id=c.id,
                author=to_user_out(users[c.author_id]),
                body=c.body,
                created_at=as_utc(c.created_at),
            )
            for c in comments
        ],
        available_transitions=available_transitions(config, case, current_user, events),
        can_comment=has_permission(Role(current_user.role), Permission.CASE_COMMENT),
        can_assign_others=has_permission(
            Role(current_user.role), Permission.CASE_ASSIGN_OTHERS
        ),
        can_claim=has_permission(Role(current_user.role), Permission.CASE_CLAIM),
    )


def record_event(
    session: Session,
    case: Case,
    *,
    kind: str,
    actor_id: str | None,
    transition_key: str | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    reason_code: str | None = None,
    note: str | None = None,
    meta: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> CaseEvent:
    event = CaseEvent(
        id=new_id("evt"),
        case_id=case.id,
        actor_id=actor_id,
        kind=kind,
        transition_key=transition_key,
        from_status=from_status,
        to_status=to_status,
        reason_code=reason_code,
        note=note,
        created_at=created_at or now(),
        meta=meta or {},
    )
    session.add(event)
    return event


def apply_transition(
    session: Session,
    config: CaseTypeConfig,
    case: Case,
    user: User,
    *,
    transition_key: str,
    note: str | None,
    reason_code: str | None,
) -> Case:
    transition = config.transition(transition_key)
    if transition is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Unknown transition '{transition_key}'."
        )

    events = list(
        session.exec(select(CaseEvent).where(CaseEvent.case_id == case.id)).all()
    )
    blocked = _transition_blocked_reason(config, transition, case, user, events)
    if blocked:
        raise HTTPException(status.HTTP_403_FORBIDDEN, blocked)
    if transition.requires_note and not (note or "").strip():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "A note is required.")
    if transition.requires_reason_code:
        valid = {r.key for r in transition.reason_codes}
        if reason_code not in valid:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "A valid reason code is required."
            )

    from_status = case.status
    case.status = transition.to_state
    if transition.assigns_to_actor:
        case.assignee_id = user.id
    target_state = config.state(transition.to_state)
    case.closed_at = now() if target_state and target_state.terminal else None

    record_event(
        session,
        case,
        kind="transition",
        actor_id=user.id,
        transition_key=transition.key,
        from_status=from_status,
        to_status=transition.to_state,
        reason_code=reason_code,
        note=note,
    )
    session.add(case)
    session.commit()
    session.refresh(case)
    return case


def add_comment(session: Session, case: Case, user: User, body: str) -> Comment:
    if not body.strip():
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Comment cannot be empty."
        )
    comment = Comment(
        id=new_id("cmt"),
        case_id=case.id,
        author_id=user.id,
        body=body.strip(),
        created_at=now(),
    )
    session.add(comment)
    record_event(
        session, case, kind="comment", actor_id=user.id, note=body.strip()[:160]
    )
    session.commit()
    session.refresh(comment)
    return comment


def assign_case(
    session: Session,
    case: Case,
    user: User,
    assignee_id: str | None,
) -> Case:
    previous = case.assignee_id
    case.assignee_id = assignee_id
    assignee = session.get(User, assignee_id) if assignee_id else None
    record_event(
        session,
        case,
        kind="assignment",
        actor_id=user.id,
        note=f"Assigned to {assignee.name}" if assignee else "Unassigned",
        meta={"from": previous, "to": assignee_id},
    )
    session.add(case)
    session.commit()
    session.refresh(case)
    return case


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------


def metrics(session: Session, config: CaseTypeConfig, current_user: User) -> MetricsOut:
    cases = session.exec(select(Case).where(Case.case_type == config.key)).all()
    reference_time = now()
    open_states = set(config.open_states())
    open_cases = [c for c in cases if c.status in open_states]
    overdue = [c for c in open_cases if c.due_at < reference_time]
    mine = [c for c in open_cases if c.assignee_id == current_user.id]
    pending_approval = [c for c in cases if c.status == "pending_approval"]
    closed = [c for c in cases if c.closed_at is not None]
    cycle_hours = [
        (c.closed_at - c.opened_at).total_seconds() / 3600
        for c in closed
        if c.closed_at
    ]
    median_cycle = 0.0
    if cycle_hours:
        ordered = sorted(cycle_hours)
        median_cycle = round(ordered[len(ordered) // 2], 1)
    sar_rate = (
        round(100 * len([c for c in cases if c.status == "sar_filed"]) / len(closed), 1)
        if closed
        else 0.0
    )

    tiles = [
        MetricTileOut(
            key="open",
            label="Open alerts",
            value=len(open_cases),
            format="number",
            hint=f"{len(mine)} assigned to you",
        ),
        MetricTileOut(
            key="overdue",
            label="Breaching SLA",
            value=len(overdue),
            format="number",
            tone="danger" if overdue else "success",
            hint=f"{config.sla_hours}h target",
        ),
        MetricTileOut(
            key="pending_approval",
            label="Awaiting approval",
            value=len(pending_approval),
            format="number",
            tone="warn" if pending_approval else "neutral",
            hint="SAR recommendations",
        ),
        MetricTileOut(
            key="cycle",
            label="Median time to close",
            value=median_cycle,
            format="hours",
            hint=f"across {len(closed)} closed alerts",
        ),
        MetricTileOut(
            key="sar_rate",
            label="SAR conversion",
            value=sar_rate,
            format="percent",
            hint="of closed alerts",
        ),
    ]

    by_status = [
        BreakdownItemOut(
            key=state.key,
            label=state.label,
            value=len([c for c in cases if c.status == state.key]),
            tone=state.tone,
        )
        for state in config.states
    ]

    typology_counts = Counter(
        c.payload.get("typology_label", "Unclassified") for c in cases if c.payload
    )
    by_typology = [
        BreakdownItemOut(key=label, label=label, value=count)
        for label, count in typology_counts.most_common()
    ]

    trend: list[TrendPointOut] = []
    for offset in range(13, -1, -1):
        day = (reference_time - timedelta(days=offset)).date()
        trend.append(
            TrendPointOut(
                date=day.isoformat(),
                opened=len([c for c in cases if c.opened_at.date() == day]),
                closed=len(
                    [c for c in cases if c.closed_at and c.closed_at.date() == day]
                ),
            )
        )

    return MetricsOut(
        tiles=tiles, by_status=by_status, by_typology=by_typology, trend=trend
    )


def users_out(session: Session) -> list[UserOut]:
    users = session.exec(select(User)).all()
    return [to_user_out(u) for u in sorted(users, key=lambda u: u.name)]
