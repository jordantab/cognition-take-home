"""Queue metrics."""

from __future__ import annotations

from datetime import timedelta

import pytest

from tests.conftest import NOW


def headers(users, role: str) -> dict[str, str]:
    return {"X-User-Id": users[role].id}


@pytest.fixture(name="metrics")
def metrics_fixture(client, users, make_case):
    make_case(status="new")
    make_case(status="in_review", assignee=users["analyst"])
    make_case(
        status="in_review",
        opened_at=NOW - timedelta(days=8),
        due_at=NOW - timedelta(days=5),
    )
    make_case(status="pending_approval")
    make_case(
        status="closed_no_action",
        opened_at=NOW - timedelta(hours=30),
        closed_at=NOW - timedelta(hours=20),
    )
    make_case(
        status="sar_filed",
        opened_at=NOW - timedelta(hours=60),
        closed_at=NOW - timedelta(hours=10),
    )

    def fetch(role: str = "analyst"):
        response = client.get(
            "/api/case-types/aml/metrics", headers=headers(users, role)
        )
        assert response.status_code == 200, response.text
        return response.json()

    return fetch


def tile(payload, key: str):
    return next(t for t in payload["tiles"] if t["key"] == key)


def test_open_and_overdue_counts_exclude_terminal_states(metrics):
    payload = metrics()
    assert tile(payload, "open")["value"] == 4
    assert tile(payload, "overdue")["value"] == 1
    assert tile(payload, "overdue")["tone"] == "danger"


def test_the_open_tile_is_scoped_to_the_viewer(metrics, users):
    assert "1 assigned to you" in tile(metrics("analyst"), "open")["hint"]
    assert "0 assigned to you" in tile(metrics("compliance_manager"), "open")["hint"]


def test_cycle_time_and_sar_conversion_are_computed_over_closed_cases(metrics):
    payload = metrics()
    assert tile(payload, "cycle")["value"] == 50.0
    assert tile(payload, "sar_rate")["value"] == 50.0
    assert tile(payload, "pending_approval")["value"] == 1


def test_breakdowns_cover_every_declared_state(metrics, aml):
    payload = metrics()
    assert [b["key"] for b in payload["by_status"]] == [s.key for s in aml.states]
    assert sum(b["value"] for b in payload["by_status"]) == 6
    assert {b["label"] for b in payload["by_typology"]} == {"Structuring"}


def test_the_trend_covers_the_last_fourteen_days(metrics):
    payload = metrics()
    assert len(payload["trend"]) == 14
    assert sum(p["closed"] for p in payload["trend"]) == 2
    assert payload["trend"] == sorted(payload["trend"], key=lambda p: p["date"])


def test_metrics_on_an_empty_queue_do_not_divide_by_zero(client, users):
    payload = client.get(
        "/api/case-types/aml/metrics", headers=headers(users, "analyst")
    ).json()
    assert [t["value"] for t in payload["tiles"]] == [0, 0, 0, 0.0, 0.0]
