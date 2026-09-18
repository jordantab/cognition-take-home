"""The audit log is append-only and records every state change."""

from __future__ import annotations

from sqlmodel import select

from app.core.models import CaseEvent


def headers(users, role: str) -> dict[str, str]:
    return {"X-User-Id": users[role].id}


def events(session, case) -> list[CaseEvent]:
    return list(
        session.exec(select(CaseEvent).where(CaseEvent.case_id == case.id)).all()
    )


def test_a_transition_appends_an_event_describing_it(client, session, users, make_case):
    case = make_case(status="in_review")
    client.post(
        f"/api/cases/{case.id}/transition",
        json={
            "transition": "close_no_action",
            "note": "Consistent with the customer's trading history.",
            "reason_code": "expected_activity",
        },
        headers=headers(users, "analyst"),
    )

    (event,) = events(session, case)
    assert (event.kind, event.transition_key) == ("transition", "close_no_action")
    assert (event.from_status, event.to_status) == ("in_review", "closed_no_action")
    assert event.actor_id == users["analyst"].id
    assert event.reason_code == "expected_activity"
    assert event.note == "Consistent with the customer's trading history."


def test_assignments_and_comments_are_audited(client, session, users, make_case):
    case = make_case(status="new")
    client.post(
        f"/api/cases/{case.id}/assignee",
        json={"assignee_id": users["analyst"].id},
        headers=headers(users, "senior_analyst"),
    )
    client.post(
        f"/api/cases/{case.id}/comments",
        json={"body": "Pulled the RFI response."},
        headers=headers(users, "analyst"),
    )

    kinds = [e.kind for e in events(session, case)]
    assert kinds == ["assignment", "comment"]

    assignment = events(session, case)[0]
    assert assignment.meta == {"from": None, "to": users["analyst"].id}


def test_a_rejected_transition_writes_nothing(client, session, users, make_case):
    case = make_case(status="in_review")
    response = client.post(
        f"/api/cases/{case.id}/transition",
        json={"transition": "file_sar", "note": "Filing."},
        headers=headers(users, "analyst"),
    )
    assert response.status_code == 403
    assert events(session, case) == []


def test_history_is_append_only_across_a_full_investigation(
    client, session, users, make_case
):
    case = make_case(status="new")
    steps = [
        ("analyst", {"transition": "claim"}),
        (
            "analyst",
            {"transition": "request_info", "note": "RFI sent for source of funds."},
        ),
        ("analyst", {"transition": "resume"}),
        (
            "analyst",
            {
                "transition": "recommend_sar",
                "note": "Layering across three accounts.",
                "reason_code": "structuring",
            },
        ),
        (
            "compliance_manager",
            {"transition": "file_sar", "note": "Narrative reviewed; filed."},
        ),
    ]

    seen: list[str] = []
    for role, body in steps:
        response = client.post(
            f"/api/cases/{case.id}/transition", json=body, headers=headers(users, role)
        )
        assert response.status_code == 200, response.text
        current = events(session, case)
        # Nothing already written is edited or removed as history grows.
        assert [e.id for e in current][: len(seen)] == seen
        seen = [e.id for e in current]

    assert [e.transition_key for e in events(session, case)] == [
        "claim",
        "request_info",
        "resume",
        "recommend_sar",
        "file_sar",
    ]


def test_the_detail_endpoint_labels_events_from_the_declaration(
    client, users, make_case
):
    case = make_case(status="in_review")
    client.post(
        f"/api/cases/{case.id}/transition",
        json={
            "transition": "close_no_action",
            "note": "Duplicate.",
            "reason_code": "duplicate_alert",
        },
        headers=headers(users, "analyst"),
    )

    detail = client.get(
        f"/api/cases/{case.id}", headers=headers(users, "analyst")
    ).json()
    (event,) = detail["events"]
    assert event["transition_label"] == "Close - no action"
    assert event["reason_label"] == "Duplicate of another alert"
    assert event["actor"]["id"] == users["analyst"].id
