"""Deterministic demo data.

Run with `make seed`. The same seed always produces the same customers,
transactions, alerts and audit trails, so demos and screenshots are stable.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

from faker import Faker
from sqlmodel import Session, delete

import app.casetypes.aml  # noqa: F401  (registers the AML case type)
from app.casetypes.aml import CLOSE_REASONS, TYPOLOGIES
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
from app.core.service import new_id
from app.db import create_db_and_tables, engine
from app.settings import SEED

fake = Faker("en_US")

HIGH_RISK_COUNTRIES = ["PA", "CY", "AE", "LB", "BY", "MM", "KY", "SC"]
HOME_COUNTRIES = ["US", "US", "US", "US", "CA", "GB", "DE", "SG"]
CHANNELS = ["wire", "ach", "card", "cash", "crypto_offramp"]
SEGMENTS = ["Consumer", "Small business", "Mid-market", "Platform partner"]
OCCUPATIONS = [
    "Freelance consultant",
    "Retail owner",
    "Software engineer",
    "Import/export broker",
    "Real estate agent",
    "Restaurant operator",
    "Logistics manager",
    "Crypto trader",
]
SANCTIONS_NAMES = [
    "Viktor Anatolyev",
    "Global Maritime Trading FZE",
    "Nadia Kerimova",
    "Delta Horizon Shipping",
    "Aleksei Morozov",
]

USERS = [
    (
        "usr_amelia",
        "Amelia Ortiz",
        "analyst",
        "Financial Crime Analyst",
        "Financial Crime",
    ),
    ("usr_dev", "Dev Raman", "analyst", "Financial Crime Analyst", "Financial Crime"),
    (
        "usr_priya",
        "Priya Nair",
        "senior_analyst",
        "Senior Investigator",
        "Financial Crime",
    ),
    (
        "usr_marcus",
        "Marcus Webb",
        "compliance_manager",
        "Head of Compliance",
        "Compliance",
    ),
    ("usr_sofia", "Sofia Lindqvist", "ops_agent", "Payment Operations", "Operations"),
    ("usr_admin", "Rae Patel", "admin", "Platform Admin", "Engineering"),
]

RULES = {
    "structuring": ("RULE-114", "Multiple sub-threshold cash deposits"),
    "rapid_movement": ("RULE-207", "Funds in / funds out within 48 hours"),
    "high_risk_geo": ("RULE-309", "Wire exposure to high-risk jurisdiction"),
    "sanctions_nexus": ("RULE-401", "Counterparty name screening hit"),
    "unusual_for_profile": ("RULE-512", "Volume anomaly versus customer profile"),
    "third_party_funding": ("RULE-618", "Inbound funding from unrelated third party"),
}

STATUS_WEIGHTS = [
    ("new", 22),
    ("in_review", 24),
    ("awaiting_info", 8),
    ("pending_approval", 11),
    ("closed_no_action", 27),
    ("sar_filed", 8),
]

ANALYST_NOTES = [
    "Reviewed 90 days of activity; pattern is inconsistent with the stated occupation.",
    "Counterparty resolves to a shell entity with no discernible operating history.",
    "Customer provided invoices covering the inbound wires; documentation looks consistent.",
    "Deposits align with the seasonal cash cycle of the registered business.",
    "No adverse media. Source of funds corroborated by payroll records.",
    "Escalating: layering pattern across three accounts opened within the same week.",
]

COMMENT_BODIES = [
    "Pulled the last two RFI responses, attaching the summary here.",
    "Checked the related alert from last quarter - same counterparty, different account.",
    "Ops confirmed the wire reference matches an invoice in the merchant portal.",
    "This looks like the same typology we saw in the March cluster.",
    "Customer relationship manager says the business expanded into a new market.",
]


def _pick(rng: random.Random, weights: list[tuple[str, int]]) -> str:
    population = [value for value, _ in weights]
    weight_values = [weight for _, weight in weights]
    return rng.choices(population, weights=weight_values, k=1)[0]


def wipe(session: Session) -> None:
    for model in (
        CaseEvent,
        Comment,
        Case,
        Transaction,
        Account,
        WatchlistHit,
        Customer,
        User,
    ):
        session.exec(delete(model))
    session.commit()


def seed() -> None:
    rng = random.Random(SEED)
    Faker.seed(SEED)
    create_db_and_tables()
    now = datetime.now(UTC).replace(tzinfo=None, microsecond=0)

    with Session(engine) as session:
        wipe(session)

        users = [
            User(
                id=uid,
                name=name,
                email=f"{name.split()[0].lower()}@northwind.example",
                role=role,
                job_title=title,
                team=team,
            )
            for uid, name, role, title, team in USERS
        ]
        session.add_all(users)

        analysts = [u for u in users if u.role in {"analyst", "senior_analyst"}]
        managers = [u for u in users if u.role in {"compliance_manager", "admin"}]

        customers: list[Customer] = []
        accounts: list[Account] = []
        transactions: list[Transaction] = []

        for _ in range(140):
            is_business = rng.random() < 0.35
            name = fake.company() if is_business else fake.name()
            risk_rating = _pick(rng, [("low", 55), ("medium", 32), ("high", 13)])
            customer = Customer(
                id=new_id("cus"),
                name=name,
                kind="business" if is_business else "individual",
                country=rng.choice(HOME_COUNTRIES),
                segment=rng.choice(SEGMENTS),
                risk_rating=risk_rating,
                kyc_status=_pick(
                    rng, [("verified", 85), ("refresh_due", 12), ("pending", 3)]
                ),
                is_pep=rng.random() < 0.06,
                occupation="Registered business"
                if is_business
                else rng.choice(OCCUPATIONS),
                email=fake.email(),
                onboarded_at=now - timedelta(days=rng.randint(40, 1500)),
                lifetime_volume=round(rng.uniform(20_000, 4_000_000), 2),
            )
            customers.append(customer)

            for _ in range(rng.randint(1, 2)):
                account = Account(
                    id=new_id("acc"),
                    customer_id=customer.id,
                    number=f"****{rng.randint(1000, 9999)}",
                    kind="business_checking" if is_business else "personal_checking",
                    currency="USD",
                    balance=round(rng.uniform(500, 480_000), 2),
                    status="active",
                    opened_at=customer.onboarded_at
                    + timedelta(days=rng.randint(0, 30)),
                )
                accounts.append(account)

                for _ in range(rng.randint(12, 28)):
                    direction = _pick(rng, [("credit", 55), ("debit", 45)])
                    transactions.append(
                        Transaction(
                            id=new_id("txn"),
                            account_id=account.id,
                            customer_id=customer.id,
                            posted_at=now
                            - timedelta(
                                days=rng.randint(0, 90), hours=rng.randint(0, 23)
                            ),
                            amount=round(rng.uniform(45, 14_000), 2),
                            currency="USD",
                            direction=direction,
                            channel=_pick(
                                rng,
                                [
                                    ("ach", 40),
                                    ("card", 25),
                                    ("wire", 20),
                                    ("cash", 10),
                                    ("crypto_offramp", 5),
                                ],
                            ),
                            counterparty_name=fake.company()
                            if rng.random() < 0.6
                            else fake.name(),
                            counterparty_country=rng.choice(HOME_COUNTRIES),
                            description=rng.choice(
                                [
                                    "Invoice settlement",
                                    "Payroll",
                                    "Vendor payment",
                                    "Card purchase",
                                    "Transfer",
                                    "Refund",
                                ]
                            ),
                        )
                    )

        session.add_all(customers)
        session.add_all(accounts)

        accounts_by_customer: dict[str, list[Account]] = {}
        for account in accounts:
            accounts_by_customer.setdefault(account.customer_id, []).append(account)

        # ------------------------------------------------------------------
        # Alerts, each backed by a concrete transaction pattern
        # ------------------------------------------------------------------
        # A handful of customers get two alerts so the Related tab has content.
        alert_customers = rng.sample(customers, 58)
        alert_customers += rng.sample(alert_customers, 6)
        rng.shuffle(alert_customers)
        cases: list[Case] = []
        events: list[CaseEvent] = []
        comments: list[Comment] = []
        hits: list[WatchlistHit] = []

        for index, customer in enumerate(alert_customers, start=1):
            typology = _pick(
                rng,
                [
                    ("structuring", 26),
                    ("rapid_movement", 20),
                    ("high_risk_geo", 18),
                    ("unusual_for_profile", 16),
                    ("third_party_funding", 12),
                    ("sanctions_nexus", 8),
                ],
            )
            rule_id, rule_name = RULES[typology]
            account = accounts_by_customer[customer.id][0]
            status = _pick(rng, STATUS_WEIGHTS)
            # Open work is recent; closed work stretches further back, so the
            # queue has a believable mix of SLA breaches rather than all of them.
            age_days = {
                "new": (0, 2),
                "in_review": (0, 4),
                "awaiting_info": (1, 6),
                "pending_approval": (1, 5),
                "closed_no_action": (4, 30),
                "sar_filed": (6, 30),
            }[status]
            opened_at = now - timedelta(
                days=rng.randint(*age_days), hours=rng.randint(0, 23)
            )
            window_start = opened_at - timedelta(days=rng.randint(2, 10))
            flagged: list[Transaction] = []

            if typology == "structuring":
                count = rng.randint(4, 7)
                for i in range(count):
                    flagged.append(
                        Transaction(
                            id=new_id("txn"),
                            account_id=account.id,
                            customer_id=customer.id,
                            posted_at=window_start + timedelta(hours=8 * i),
                            amount=round(rng.uniform(8_600, 9_850), 2),
                            currency="USD",
                            direction="credit",
                            channel="cash",
                            counterparty_name="Branch deposit",
                            counterparty_country="US",
                            description=f"Cash deposit - branch {rng.randint(100, 140)}",
                            is_flagged=True,
                        )
                    )
            elif typology == "rapid_movement":
                inbound = round(rng.uniform(80_000, 420_000), 2)
                flagged.append(
                    Transaction(
                        id=new_id("txn"),
                        account_id=account.id,
                        customer_id=customer.id,
                        posted_at=window_start,
                        amount=inbound,
                        currency="USD",
                        direction="credit",
                        channel="wire",
                        counterparty_name=fake.company(),
                        counterparty_country=rng.choice(HOME_COUNTRIES),
                        description="Inbound wire",
                        is_flagged=True,
                    )
                )
                remaining = inbound
                for i in range(rng.randint(3, 5)):
                    amount = round(remaining * rng.uniform(0.18, 0.3), 2)
                    remaining -= amount
                    flagged.append(
                        Transaction(
                            id=new_id("txn"),
                            account_id=account.id,
                            customer_id=customer.id,
                            posted_at=window_start + timedelta(hours=6 + 5 * i),
                            amount=amount,
                            currency="USD",
                            direction="debit",
                            channel=rng.choice(["wire", "crypto_offramp"]),
                            counterparty_name=fake.company(),
                            counterparty_country=rng.choice(HIGH_RISK_COUNTRIES),
                            description="Outbound transfer",
                            is_flagged=True,
                        )
                    )
            elif typology == "high_risk_geo":
                for i in range(rng.randint(2, 4)):
                    flagged.append(
                        Transaction(
                            id=new_id("txn"),
                            account_id=account.id,
                            customer_id=customer.id,
                            posted_at=window_start + timedelta(days=i),
                            amount=round(rng.uniform(25_000, 190_000), 2),
                            currency="USD",
                            direction=_pick(rng, [("debit", 65), ("credit", 35)]),
                            channel="wire",
                            counterparty_name=fake.company(),
                            counterparty_country=rng.choice(HIGH_RISK_COUNTRIES),
                            description="Cross-border wire",
                            is_flagged=True,
                        )
                    )
            elif typology == "sanctions_nexus":
                matched = rng.choice(SANCTIONS_NAMES)
                flagged.append(
                    Transaction(
                        id=new_id("txn"),
                        account_id=account.id,
                        customer_id=customer.id,
                        posted_at=window_start,
                        amount=round(rng.uniform(15_000, 120_000), 2),
                        currency="USD",
                        direction="debit",
                        channel="wire",
                        counterparty_name=matched,
                        counterparty_country=rng.choice(HIGH_RISK_COUNTRIES),
                        description="Wire to screened counterparty",
                        is_flagged=True,
                    )
                )
                hits.append(
                    WatchlistHit(
                        id=new_id("hit"),
                        customer_id=customer.id,
                        list_name=rng.choice(
                            ["OFAC SDN", "EU Consolidated", "UN Sanctions"]
                        ),
                        matched_name=matched,
                        match_score=rng.randint(78, 97),
                        status="potential",
                        details="Fuzzy name match on wire counterparty; DOB not available.",
                        screened_at=window_start,
                    )
                )
            elif typology == "unusual_for_profile":
                for i in range(rng.randint(2, 3)):
                    flagged.append(
                        Transaction(
                            id=new_id("txn"),
                            account_id=account.id,
                            customer_id=customer.id,
                            posted_at=window_start + timedelta(days=i),
                            amount=round(rng.uniform(60_000, 250_000), 2),
                            currency="USD",
                            direction="credit",
                            channel=rng.choice(["wire", "ach"]),
                            counterparty_name=fake.company(),
                            counterparty_country="US",
                            description="Large inbound versus 90-day average",
                            is_flagged=True,
                        )
                    )
            else:  # third_party_funding
                for i in range(rng.randint(3, 5)):
                    flagged.append(
                        Transaction(
                            id=new_id("txn"),
                            account_id=account.id,
                            customer_id=customer.id,
                            posted_at=window_start
                            + timedelta(days=i, hours=rng.randint(0, 10)),
                            amount=round(rng.uniform(4_000, 28_000), 2),
                            currency="USD",
                            direction="credit",
                            channel="ach",
                            counterparty_name=fake.name(),
                            counterparty_country="US",
                            description="Third-party inbound transfer",
                            is_flagged=True,
                        )
                    )

            transactions.extend(flagged)
            exposure = round(sum(t.amount for t in flagged), 2)
            risk_score = min(
                99,
                int(
                    38
                    + (
                        25
                        if customer.risk_rating == "high"
                        else 10
                        if customer.risk_rating == "medium"
                        else 0
                    )
                    + (12 if customer.is_pep else 0)
                    + min(30, exposure / 20_000)
                    + rng.randint(-6, 8)
                ),
            )
            priority = (
                "high" if risk_score >= 75 else "medium" if risk_score >= 55 else "low"
            )
            sla_hours = 72
            due_at = opened_at + timedelta(hours=sla_hours)

            case = Case(
                id=new_id("case"),
                case_type="aml",
                reference=f"AML-{2400 + index}",
                title=f"{TYPOLOGIES[typology]} - {customer.name}",
                status=status,
                priority=priority,
                risk_score=risk_score,
                amount=exposure,
                currency="USD",
                subject_id=customer.id,
                assignee_id=None,
                opened_at=opened_at,
                due_at=due_at,
                closed_at=None,
                payload={
                    "typology": typology,
                    "typology_label": TYPOLOGIES[typology],
                    "rule_id": rule_id,
                    "rule_name": f"{rule_id} - {rule_name}",
                    "window_label": (
                        f"{window_start.date().isoformat()} to {opened_at.date().isoformat()}"
                    ),
                    "transaction_ids": [t.id for t in flagged],
                    "flagged_count": len(flagged),
                },
            )

            events.append(
                CaseEvent(
                    id=new_id("evt"),
                    case_id=case.id,
                    actor_id=None,
                    kind="created",
                    to_status="new",
                    note=f"Alert generated by {rule_id}",
                    created_at=opened_at,
                    meta={"rule_id": rule_id},
                )
            )

            cursor = opened_at
            analyst = rng.choice(analysts)
            if status != "new":
                # Clamped so a recent alert never gets future-dated history.
                cursor = min(cursor + timedelta(hours=rng.randint(1, 20)), now)
                case.assignee_id = analyst.id
                events.append(
                    CaseEvent(
                        id=new_id("evt"),
                        case_id=case.id,
                        actor_id=analyst.id,
                        kind="transition",
                        transition_key="claim",
                        from_status="new",
                        to_status="in_review",
                        created_at=cursor,
                        meta={},
                    )
                )

            if status == "awaiting_info":
                cursor = min(cursor + timedelta(hours=rng.randint(2, 26)), now)
                events.append(
                    CaseEvent(
                        id=new_id("evt"),
                        case_id=case.id,
                        actor_id=analyst.id,
                        kind="transition",
                        transition_key="request_info",
                        from_status="in_review",
                        to_status="awaiting_info",
                        note="RFI sent to the customer for source-of-funds documentation.",
                        created_at=cursor,
                        meta={},
                    )
                )
            elif status == "closed_no_action":
                cursor = min(cursor + timedelta(hours=rng.randint(3, 40)), now)
                reason = rng.choice(CLOSE_REASONS)
                events.append(
                    CaseEvent(
                        id=new_id("evt"),
                        case_id=case.id,
                        actor_id=analyst.id,
                        kind="transition",
                        transition_key="close_no_action",
                        from_status="in_review",
                        to_status="closed_no_action",
                        reason_code=reason.key,
                        note=rng.choice(ANALYST_NOTES),
                        created_at=cursor,
                        meta={},
                    )
                )
                case.closed_at = cursor
            elif status in {"pending_approval", "sar_filed"}:
                cursor = min(cursor + timedelta(hours=rng.randint(4, 36)), now)
                events.append(
                    CaseEvent(
                        id=new_id("evt"),
                        case_id=case.id,
                        actor_id=analyst.id,
                        kind="transition",
                        transition_key="recommend_sar",
                        from_status="in_review",
                        to_status="pending_approval",
                        reason_code=typology,
                        note=rng.choice(ANALYST_NOTES),
                        created_at=cursor,
                        meta={},
                    )
                )
                if status == "sar_filed":
                    manager = rng.choice(managers)
                    cursor = min(cursor + timedelta(hours=rng.randint(2, 30)), now)
                    events.append(
                        CaseEvent(
                            id=new_id("evt"),
                            case_id=case.id,
                            actor_id=manager.id,
                            kind="transition",
                            transition_key="file_sar",
                            from_status="pending_approval",
                            to_status="sar_filed",
                            note="Reviewed the narrative and supporting transactions; SAR filed.",
                            created_at=cursor,
                            meta={
                                "filing_reference": f"FIN-{rng.randint(100000, 999999)}"
                            },
                        )
                    )
                    case.closed_at = cursor

            for _ in range(rng.randint(0, 3)):
                author = rng.choice(users[:4])
                comment_at = min(opened_at + timedelta(hours=rng.randint(1, 60)), now)
                comments.append(
                    Comment(
                        id=new_id("cmt"),
                        case_id=case.id,
                        author_id=author.id,
                        body=rng.choice(COMMENT_BODIES),
                        created_at=comment_at,
                    )
                )

            cases.append(case)

        # Unrelated screening noise so the Screening tab is not always empty.
        for customer in rng.sample(customers, 18):
            hits.append(
                WatchlistHit(
                    id=new_id("hit"),
                    customer_id=customer.id,
                    list_name=rng.choice(
                        ["Adverse Media", "PEP Register", "Internal Blocklist"]
                    ),
                    matched_name=customer.name,
                    match_score=rng.randint(55, 84),
                    status=_pick(rng, [("discounted", 70), ("potential", 30)]),
                    details="Screened during periodic refresh.",
                    screened_at=now - timedelta(days=rng.randint(5, 200)),
                )
            )

        session.add_all(transactions)
        session.add_all(cases)
        session.add_all(events)
        session.add_all(comments)
        session.add_all(hits)
        session.commit()

        print(
            f"Seeded {len(users)} users, {len(customers)} customers, "
            f"{len(accounts)} accounts, {len(transactions)} transactions, "
            f"{len(cases)} AML alerts, {len(events)} audit events."
        )


if __name__ == "__main__":
    seed()
