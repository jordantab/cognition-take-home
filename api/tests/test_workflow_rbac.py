"""Workflow and RBAC enforcement, driven from the AML declaration.

The point of these tests is that the *engine* enforces what the declaration
says, so they read `TRANSITIONS` rather than restating it.
"""

from __future__ import annotations

import pytest

from app.casetypes.aml import TRANSITIONS
from app.core.rbac import PERMISSIONS, Role
from app.core.workflow import Transition

ROLES = [r.value for r in Role]


def headers(users, role: str) -> dict[str, str]:
    return {"X-User-Id": users[role].id}


def transition(key: str) -> Transition:
    found = next(t for t in TRANSITIONS if t.key == key)
    return found


def payload_for(t: Transition) -> dict[str, str]:
    body: dict[str, str] = {"transition": t.key}
    if t.requires_note:
        body["note"] = "Documented rationale for the decision."
    if t.requires_reason_code:
        body["reason_code"] = t.reason_codes[0].key
    return body


@pytest.mark.parametrize("t", TRANSITIONS, ids=lambda t: t.key)
@pytest.mark.parametrize("role", ROLES)
def test_transition_allowed_exactly_for_roles_holding_the_permission(
    client, users, make_case, t: Transition, role: str
):
    """Every declared transition is gated by its declared permission."""
    case = make_case(status=t.from_states[0], assignee=users[role])
    response = client.post(
        f"/api/cases/{case.id}/transition",
        json=payload_for(t),
        headers=headers(users, role),
    )
    permitted = t.permission in PERMISSIONS[Role(role)]
    if permitted:
        assert response.status_code == 200, response.text
        assert response.json()["case"]["status"] == t.to_state
    else:
        assert response.status_code == 403, response.text
        assert t.permission in response.json()["detail"]


@pytest.mark.parametrize("t", TRANSITIONS, ids=lambda t: t.key)
def test_transition_rejected_from_a_state_it_does_not_declare(
    client, users, make_case, t: Transition
):
    """`from_states` is enforced, not just used to render buttons."""
    other = next(
        s
        for s in ("new", "in_review", "awaiting_info", "pending_approval", "sar_filed")
        if s not in t.from_states
    )
    case = make_case(status=other)
    response = client.post(
        f"/api/cases/{case.id}/transition",
        json=payload_for(t),
        headers=headers(users, "admin"),
    )
    assert response.status_code == 403
    assert "current status" in response.json()["detail"]


@pytest.mark.parametrize(
    "t", [t for t in TRANSITIONS if t.requires_note], ids=lambda t: t.key
)
@pytest.mark.parametrize("note", [None, "", "   "])
def test_transition_requiring_a_note_rejects_a_blank_one(
    client, users, make_case, t: Transition, note
):
    case = make_case(status=t.from_states[0])
    body = payload_for(t) | {"note": note}
    response = client.post(
        f"/api/cases/{case.id}/transition", json=body, headers=headers(users, "admin")
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "A note is required."


@pytest.mark.parametrize(
    "t", [t for t in TRANSITIONS if t.requires_reason_code], ids=lambda t: t.key
)
@pytest.mark.parametrize("reason_code", [None, "not_a_reason_code"])
def test_transition_requiring_a_reason_code_rejects_an_unknown_one(
    client, users, make_case, t: Transition, reason_code
):
    case = make_case(status=t.from_states[0])
    body = payload_for(t) | {"reason_code": reason_code}
    response = client.post(
        f"/api/cases/{case.id}/transition", json=body, headers=headers(users, "admin")
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "A valid reason code is required."


def recommend(client, users, case, role: str = "senior_analyst"):
    return client.post(
        f"/api/cases/{case.id}/transition",
        json=payload_for(transition("recommend_sar")),
        headers=headers(users, role),
    )


def test_four_eyes_blocks_the_recommending_actor_from_approving(
    client, users, make_case
):
    case = make_case(status="in_review")
    assert recommend(client, users, case, role="admin").status_code == 200

    response = client.post(
        f"/api/cases/{case.id}/transition",
        json=payload_for(transition("file_sar")),
        headers=headers(users, "admin"),
    )
    assert response.status_code == 403
    assert "Four-eyes" in response.json()["detail"]


def test_four_eyes_allows_a_different_approver(client, users, make_case):
    case = make_case(status="in_review")
    assert recommend(client, users, case).status_code == 200

    response = client.post(
        f"/api/cases/{case.id}/transition",
        json=payload_for(transition("file_sar")),
        headers=headers(users, "compliance_manager"),
    )
    assert response.status_code == 200
    assert response.json()["case"]["status"] == "sar_filed"


def test_four_eyes_is_reported_on_the_available_transitions(client, users, make_case):
    case = make_case(status="in_review")
    recommend(client, users, case, role="admin")

    detail = client.get(f"/api/cases/{case.id}", headers=headers(users, "admin")).json()
    file_sar = next(
        t for t in detail["available_transitions"] if t["key"] == "file_sar"
    )
    assert file_sar["enabled"] is False
    assert "Four-eyes" in file_sar["disabled_reason"]


def test_claim_assigns_the_case_to_the_actor(client, users, make_case):
    case = make_case(status="new")
    response = client.post(
        f"/api/cases/{case.id}/transition",
        json={"transition": "claim"},
        headers=headers(users, "analyst"),
    )
    assert response.status_code == 200
    assert response.json()["case"]["assignee"]["id"] == users["analyst"].id


def test_terminal_states_close_the_case_and_reopening_clears_the_closure(
    client, users, make_case
):
    case = make_case(status="in_review")
    closed = client.post(
        f"/api/cases/{case.id}/transition",
        json=payload_for(transition("close_no_action")),
        headers=headers(users, "analyst"),
    ).json()["case"]
    assert closed["status"] == "closed_no_action"
    assert closed["closed_at"] is not None

    reopened = client.post(
        f"/api/cases/{case.id}/transition",
        json=payload_for(transition("reopen")),
        headers=headers(users, "compliance_manager"),
    ).json()["case"]
    assert reopened["status"] == "in_review"
    assert reopened["closed_at"] is None


def test_a_filed_sar_offers_no_further_transitions(client, users, make_case):
    case = make_case(status="sar_filed")
    detail = client.get(f"/api/cases/{case.id}", headers=headers(users, "admin")).json()
    assert detail["available_transitions"] == []


@pytest.mark.parametrize("role", ROLES)
def test_available_transitions_match_what_the_server_accepts(
    client, users, make_case, role: str
):
    """Frontend gating is only an affordance: it must not diverge from the API."""
    for state in ("new", "in_review", "awaiting_info", "pending_approval"):
        case = make_case(status=state)
        detail = client.get(
            f"/api/cases/{case.id}", headers=headers(users, role)
        ).json()
        for offered in detail["available_transitions"]:
            fresh = make_case(status=state)
            response = client.post(
                f"/api/cases/{fresh.id}/transition",
                json=payload_for(transition(offered["key"])),
                headers=headers(users, role),
            )
            assert (response.status_code == 200) is offered["enabled"], (
                f"{role} / {state} / {offered['key']}: {response.text}"
            )


def test_unknown_transition_is_a_404(client, users, make_case):
    case = make_case(status="new")
    response = client.post(
        f"/api/cases/{case.id}/transition",
        json={"transition": "teleport"},
        headers=headers(users, "admin"),
    )
    assert response.status_code == 404


def test_unknown_persona_is_rejected(client, make_case):
    case = make_case()
    response = client.get(f"/api/cases/{case.id}", headers={"X-User-Id": "usr_nobody"})
    assert response.status_code == 401


def test_ops_agent_can_comment_but_not_claim(client, users, make_case):
    case = make_case(status="new")
    assert (
        client.post(
            f"/api/cases/{case.id}/comments",
            json={"body": "Wire reference matches the merchant portal."},
            headers=headers(users, "ops_agent"),
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/cases/{case.id}/assignee",
            json={"assignee_id": users["ops_agent"].id},
            headers=headers(users, "ops_agent"),
        ).status_code
        == 403
    )


def test_assigning_someone_else_needs_the_assign_others_permission(
    client, users, make_case
):
    case = make_case(status="new")
    for role, expected in (("analyst", 403), ("senior_analyst", 200)):
        response = client.post(
            f"/api/cases/{case.id}/assignee",
            json={"assignee_id": users["compliance_manager"].id},
            headers=headers(users, role),
        )
        assert response.status_code == expected, response.text


def test_an_analyst_can_assign_the_case_to_themselves(client, users, make_case):
    case = make_case(status="new")
    response = client.post(
        f"/api/cases/{case.id}/assignee",
        json={"assignee_id": users["analyst"].id},
        headers=headers(users, "analyst"),
    )
    assert response.status_code == 200
    assert response.json()["case"]["assignee"]["id"] == users["analyst"].id


def test_empty_comments_are_rejected(client, users, make_case):
    case = make_case()
    response = client.post(
        f"/api/cases/{case.id}/comments",
        json={"body": "   "},
        headers=headers(users, "analyst"),
    )
    assert response.status_code == 422
