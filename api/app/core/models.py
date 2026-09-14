"""Storage model for the case platform.

`Case`, `CaseEvent` and `Comment` are case-type agnostic: anything specific to a
case type lives in `Case.payload`. The entity tables below are the mocked
fintech data warehouse the cases point at.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlalchemy import Column as SAColumn
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    name: str
    email: str
    role: str
    job_title: str
    team: str


class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: str = Field(primary_key=True)
    name: str
    kind: str  # individual | business
    country: str
    segment: str
    risk_rating: str  # low | medium | high
    kyc_status: str
    is_pep: bool = False
    occupation: str
    email: str
    onboarded_at: datetime
    lifetime_volume: float = 0.0


class Account(SQLModel, table=True):
    __tablename__ = "accounts"

    id: str = Field(primary_key=True)
    customer_id: str = Field(foreign_key="customers.id", index=True)
    number: str
    kind: str
    currency: str
    balance: float
    status: str
    opened_at: datetime


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: str = Field(primary_key=True)
    account_id: str = Field(foreign_key="accounts.id", index=True)
    customer_id: str = Field(foreign_key="customers.id", index=True)
    posted_at: datetime = Field(index=True)
    amount: float
    currency: str
    direction: str  # credit | debit
    channel: str  # wire | ach | card | crypto_offramp | cash
    counterparty_name: str
    counterparty_country: str
    description: str
    is_flagged: bool = False


class WatchlistHit(SQLModel, table=True):
    __tablename__ = "watchlist_hits"

    id: str = Field(primary_key=True)
    customer_id: str = Field(foreign_key="customers.id", index=True)
    list_name: str
    matched_name: str
    match_score: int
    status: str  # potential | discounted | confirmed
    details: str
    screened_at: datetime


class Case(SQLModel, table=True):
    __tablename__ = "cases"

    id: str = Field(primary_key=True)
    case_type: str = Field(index=True)
    reference: str = Field(index=True)
    title: str
    status: str = Field(index=True)
    priority: str = Field(index=True)
    risk_score: int = 0
    amount: float = 0.0
    currency: str = "USD"
    subject_id: str | None = Field(default=None, foreign_key="customers.id", index=True)
    assignee_id: str | None = Field(default=None, foreign_key="users.id", index=True)
    opened_at: datetime = Field(index=True)
    due_at: datetime = Field(index=True)
    closed_at: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=SAColumn(JSON))


class CaseEvent(SQLModel, table=True):
    """Append-only audit log. Every state change and assignment lands here."""

    __tablename__ = "case_events"

    id: str = Field(primary_key=True)
    case_id: str = Field(foreign_key="cases.id", index=True)
    actor_id: str | None = Field(default=None, foreign_key="users.id")
    kind: str  # created | transition | assignment | comment | system
    transition_key: str | None = None
    from_status: str | None = None
    to_status: str | None = None
    reason_code: str | None = None
    note: str | None = None
    created_at: datetime = Field(index=True)
    meta: dict[str, Any] = Field(default_factory=dict, sa_column=SAColumn(JSON))


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: str = Field(primary_key=True)
    case_id: str = Field(foreign_key="cases.id", index=True)
    author_id: str = Field(foreign_key="users.id")
    body: str
    created_at: datetime = Field(index=True)
