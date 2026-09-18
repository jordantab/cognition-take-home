"""The seed is a fixture: re-running it must reproduce the same dataset."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

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
from app.seed.seed import seed

FIXED_NOW = datetime(2026, 5, 4, 9, 30, tzinfo=UTC).replace(tzinfo=None)
MODELS = (User, Customer, Account, Transaction, WatchlistHit, Case, CaseEvent, Comment)


def fingerprint(session: Session) -> str:
    digest = hashlib.sha256()
    for model in MODELS:
        for row in session.exec(select(model).order_by(model.id)).all():
            digest.update(repr(sorted(row.model_dump().items())).encode())
    return digest.hexdigest()


def build(now: datetime) -> Session:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    seed(session, now=now, quiet=True)
    return session


def test_seeding_twice_produces_an_identical_dataset():
    assert fingerprint(build(FIXED_NOW)) == fingerprint(build(FIXED_NOW))


def test_reseeding_replaces_rather_than_duplicates(session):
    seed(session, now=FIXED_NOW, quiet=True)
    first = fingerprint(session)
    seed(session, now=FIXED_NOW, quiet=True)
    assert fingerprint(session) == first


def test_the_seeded_history_is_consistent_with_each_case_status(seeded_session, aml):
    cases = seeded_session.exec(select(Case)).all()
    events = seeded_session.exec(select(CaseEvent)).all()
    by_case: dict[str, list[CaseEvent]] = {}
    for event in events:
        by_case.setdefault(event.case_id, []).append(event)

    for case in cases:
        history = sorted(by_case[case.id], key=lambda e: e.created_at)
        assert history[0].kind == "created"
        last_status = next(
            (e.to_status for e in reversed(history) if e.to_status), "new"
        )
        assert last_status == case.status, case.reference

        state = aml.state(case.status)
        assert state is not None
        assert (case.closed_at is not None) == state.terminal, case.reference
        assert all(e.created_at >= case.opened_at for e in history), case.reference


def test_seeded_transitions_are_legal_under_the_declaration(seeded_session, aml):
    events = seeded_session.exec(
        select(CaseEvent).where(CaseEvent.kind == "transition")
    ).all()
    assert events
    for event in events:
        transition = aml.transition(event.transition_key)
        assert transition is not None, event.transition_key
        assert event.from_status in transition.from_states
        assert event.to_status == transition.to_state


def test_the_seeded_personas_cover_the_demo_workflow(seeded_session):
    roles = {u.role for u in seeded_session.exec(select(User)).all()}
    assert {"analyst", "senior_analyst", "compliance_manager"} <= roles


def test_every_alert_points_at_evidence(seeded_session):
    cases = seeded_session.exec(select(Case)).all()
    transaction_ids = {t.id for t in seeded_session.exec(select(Transaction)).all()}
    for case in cases:
        flagged = case.payload["transaction_ids"]
        assert flagged, case.reference
        assert set(flagged) <= transaction_ids, case.reference
        assert case.subject_id is not None
