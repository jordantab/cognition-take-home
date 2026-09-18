"""Shared fixtures.

Every test runs against its own in-memory database: the app's session
dependency is overridden, so nothing touches the SQLite file the demo uses.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.casetypes.aml  # registers the AML case type
from app.core.models import Case, Customer, User
from app.core.service import new_id
from app.core.workflow import CaseTypeConfig, get_case_type
from app.db import get_session
from app.main import app
from app.seed.seed import seed

PERSONAS = [
    ("usr_analyst", "Amelia Analyst", "analyst"),
    ("usr_senior", "Priya Senior", "senior_analyst"),
    ("usr_manager", "Marcus Manager", "compliance_manager"),
    ("usr_ops", "Otto Ops", "ops_agent"),
    ("usr_admin", "Ada Admin", "admin"),
]

NOW = datetime.now(UTC).replace(tzinfo=None, microsecond=0)


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Iterator[Session]:
    with Session(engine) as session:
        yield session


@pytest.fixture(name="users")
def users_fixture(session: Session) -> dict[str, User]:
    users = {
        role: User(
            id=uid,
            name=name,
            email=f"{uid}@example.test",
            role=role,
            job_title=name,
            team="Financial Crime",
        )
        for uid, name, role in PERSONAS
    }
    session.add_all(users.values())
    session.commit()
    return users


@pytest.fixture(name="client")
def client_fixture(session: Session, users: dict[str, User]) -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="aml")
def aml_fixture() -> CaseTypeConfig:
    config = get_case_type("aml")
    assert config is not None
    return config


@pytest.fixture(name="make_case")
def make_case_fixture(session: Session):
    """Build an AML case without running the full seed."""

    counter = {"n": 0}

    def factory(
        *,
        status: str = "new",
        assignee: User | None = None,
        priority: str = "medium",
        amount: float = 50_000.0,
        typology: str = "structuring",
        subject: Customer | None = None,
        opened_at: datetime | None = None,
        due_at: datetime | None = None,
        closed_at: datetime | None = None,
    ) -> Case:
        counter["n"] += 1
        opened_at = opened_at or NOW - timedelta(hours=4)
        case = Case(
            id=new_id("case"),
            case_type="aml",
            reference=f"AML-{2400 + counter['n']}",
            title=f"Test alert {counter['n']}",
            status=status,
            priority=priority,
            risk_score=60,
            amount=amount,
            currency="USD",
            subject_id=subject.id if subject else None,
            assignee_id=assignee.id if assignee else None,
            opened_at=opened_at,
            due_at=due_at or opened_at + timedelta(hours=72),
            closed_at=closed_at,
            payload={
                "typology": typology,
                "typology_label": typology.replace("_", " ").title(),
                "rule_id": "RULE-114",
                "rule_name": "RULE-114 - Multiple sub-threshold cash deposits",
                "transaction_ids": [],
                "flagged_count": 0,
            },
        )
        session.add(case)
        session.commit()
        session.refresh(case)
        return case

    return factory


@pytest.fixture(name="make_customer")
def make_customer_fixture(session: Session):
    def factory(name: str = "Acme Holdings", **overrides) -> Customer:
        customer = Customer(
            id=new_id("cus"),
            name=name,
            kind="business",
            country="US",
            segment="Consumer",
            risk_rating="medium",
            kyc_status="verified",
            is_pep=False,
            occupation="Registered business",
            email="ops@acme.test",
            onboarded_at=NOW - timedelta(days=400),
            lifetime_volume=1_000_000.0,
            **overrides,
        )
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return customer

    return factory


@pytest.fixture(scope="session")
def seeded_engine():
    """The real seed dataset, built once and shared by read-only tests."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed(session, now=NOW, quiet=True)
    return engine


@pytest.fixture(name="seeded_session")
def seeded_session_fixture(seeded_engine) -> Iterator[Session]:
    with Session(seeded_engine) as session:
        yield session
