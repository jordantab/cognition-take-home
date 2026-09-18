"""Queue listing: filters, search, sorting and paging."""

from __future__ import annotations

from datetime import timedelta

import pytest

from tests.conftest import NOW


def headers(users, role: str) -> dict[str, str]:
    return {"X-User-Id": users[role].id}


def queue(client, users, role: str = "analyst", **params):
    response = client.get(
        "/api/case-types/aml/cases", params=params, headers=headers(users, role)
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture(name="queue_data")
def queue_data_fixture(make_case, make_customer, users):
    acme = make_customer("Acme Holdings")
    borealis = make_customer("Borealis Trading")
    return {
        "new_high": make_case(
            status="new", priority="high", amount=900_000, subject=acme
        ),
        "mine": make_case(
            status="in_review",
            priority="low",
            amount=10_000,
            assignee=users["analyst"],
            typology="rapid_movement",
            subject=borealis,
        ),
        "theirs": make_case(
            status="in_review",
            priority="medium",
            amount=250_000,
            assignee=users["senior_analyst"],
        ),
        "closed": make_case(
            status="closed_no_action",
            priority="medium",
            amount=5_000,
            closed_at=NOW,
        ),
        "overdue": make_case(
            status="new",
            priority="high",
            amount=70_000,
            opened_at=NOW - timedelta(days=10),
            due_at=NOW - timedelta(days=7),
        ),
    }


def refs(payload) -> set[str]:
    return {row["reference"] for row in payload["items"]}


def test_only_cases_of_the_requested_type_are_listed(client, users, queue_data):
    payload = queue(client, users)
    assert payload["total"] == len(queue_data)
    assert all(row["case_type"] == "aml" for row in payload["items"])


def test_unknown_case_type_is_a_404(client, users):
    response = client.get(
        "/api/case-types/kyc/cases", headers=headers(users, "analyst")
    )
    assert response.status_code == 404


def test_status_filter_and_counts(client, users, queue_data):
    payload = queue(client, users, status="in_review")
    assert refs(payload) == {
        queue_data["mine"].reference,
        queue_data["theirs"].reference,
    }
    assert payload["status_counts"] == {"in_review": 2}


def test_open_only_excludes_terminal_states(client, users, queue_data):
    payload = queue(client, users, open_only=True)
    assert queue_data["closed"].reference not in refs(payload)
    assert payload["total"] == 4


def test_assignee_filter_including_unassigned(client, users, queue_data):
    mine = queue(client, users, assignee_id=users["analyst"].id)
    assert refs(mine) == {queue_data["mine"].reference}

    unassigned = queue(client, users, assignee_id="unassigned")
    assert refs(unassigned) == {
        queue_data["new_high"].reference,
        queue_data["closed"].reference,
        queue_data["overdue"].reference,
    }


def test_priority_and_typology_filters(client, users, queue_data):
    assert refs(queue(client, users, priority="high")) == {
        queue_data["new_high"].reference,
        queue_data["overdue"].reference,
    }
    assert refs(queue(client, users, typology="rapid_movement")) == {
        queue_data["mine"].reference
    }


@pytest.mark.parametrize(
    ("term", "expected_key"),
    [
        ("borealis", "mine"),  # customer name
        ("acme", "new_high"),  # customer name, different case
        ("RULE-114", "new_high"),  # triggered rule in the payload
    ],
)
def test_search_matches_reference_customer_and_rule(
    client, users, queue_data, term, expected_key
):
    assert queue_data[expected_key].reference in refs(queue(client, users, q=term))


def test_search_matches_the_case_reference_exactly(client, users, queue_data):
    reference = queue_data["mine"].reference
    assert refs(queue(client, users, q=reference)) == {reference}


def test_search_is_case_insensitive_and_trimmed(client, users, queue_data):
    assert refs(queue(client, users, q="  ACME  ")) == {
        queue_data["new_high"].reference
    }


def test_sorting_by_amount_in_both_directions(client, users, queue_data):
    ascending = [row["amount"] for row in queue(client, users, sort="amount")["items"]]
    assert ascending == sorted(ascending)

    descending = [
        row["amount"]
        for row in queue(client, users, sort="amount", direction="desc")["items"]
    ]
    assert descending == sorted(ascending, reverse=True)


def test_sorting_by_priority_uses_severity_not_alphabetical_order(
    client, users, queue_data
):
    priorities = [
        row["priority"] for row in queue(client, users, sort="priority")["items"]
    ]
    assert priorities == ["high", "high", "medium", "medium", "low"]


def test_paging_splits_the_result_without_losing_rows(client, users, queue_data):
    first = queue(client, users, sort="reference", page=1, page_size=2)
    second = queue(client, users, sort="reference", page=2, page_size=2)
    third = queue(client, users, sort="reference", page=3, page_size=2)

    assert first["total"] == second["total"] == 5
    assert len(first["items"]) == len(second["items"]) == 2
    assert len(third["items"]) == 1
    assert len(refs(first) | refs(second) | refs(third)) == 5


def test_rows_report_sla_state(client, users, queue_data):
    rows = {row["reference"]: row for row in queue(client, users)["items"]}
    assert rows[queue_data["overdue"].reference]["overdue"] is True
    assert rows[queue_data["overdue"].reference]["hours_remaining"] < 0
    assert rows[queue_data["new_high"].reference]["overdue"] is False


def test_rows_expose_the_case_type_payload_and_customer_context(
    client, users, queue_data
):
    row = next(
        r
        for r in queue(client, users)["items"]
        if r["reference"] == queue_data["new_high"].reference
    )
    assert row["subject_name"] == "Acme Holdings"
    assert row["extra"]["typology"] == "structuring"
    assert row["extra"]["customer_risk_rating"] == "medium"


def test_filters_combine(client, users, queue_data):
    payload = queue(client, users, status="in_review", priority="low")
    assert refs(payload) == {queue_data["mine"].reference}


def test_the_case_type_declaration_drives_the_queue_ui(client, users):
    declaration = client.get(
        "/api/case-types/aml", headers=headers(users, "analyst")
    ).json()
    assert next(c["key"] for c in declaration["columns"]) == "reference"
    assert {f["key"] for f in declaration["filters"]} >= {"q", "status", "priority"}

    owner_filter = next(f for f in declaration["filters"] if f["key"] == "assignee_id")
    assert {o["value"] for o in owner_filter["options"]} == {
        u.id for u in users.values()
    }


def test_presets_are_hidden_from_personas_who_cannot_use_them(client, users):
    def presets(role: str) -> set[str]:
        declaration = client.get(
            "/api/case-types/aml", headers=headers(users, role)
        ).json()
        return {p["key"] for p in declaration["presets"]}

    assert "pending_approval" not in presets("analyst")
    assert "pending_approval" in presets("compliance_manager")


def test_the_declaration_never_leaks_server_side_gating_to_the_client(client, users):
    declaration = client.get(
        "/api/case-types/aml", headers=headers(users, "analyst")
    ).json()
    for transition in declaration["transitions"]:
        assert "permission" not in transition
        assert "from_states" not in transition
