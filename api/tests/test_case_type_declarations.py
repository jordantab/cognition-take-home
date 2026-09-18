"""Contract every registered case type must satisfy.

These run over the registry, so a new app (KYC, refunds, ...) is validated the
moment its module is imported — no test changes required.
"""

from __future__ import annotations

import pytest
from sqlmodel import select

from app.core.models import Case, Customer, User
from app.core.rbac import Permission
from app.core.schemas import CaseRowOut
from app.core.service import row_out
from app.core.workflow import CaseTypeConfig, all_case_types

CASE_TYPES = all_case_types()
PARAMS = pytest.mark.parametrize("config", CASE_TYPES, ids=lambda c: c.key)

ROW_FIELDS = set(CaseRowOut.model_fields)
COLUMN_TYPES = {
    "text",
    "reference",
    "money",
    "date",
    "age",
    "risk",
    "status",
    "user",
    "priority",
    "tag",
    "sla",
}


def test_at_least_one_case_type_is_registered():
    assert CASE_TYPES


@PARAMS
def test_states_are_unique_and_include_an_open_and_a_terminal_state(
    config: CaseTypeConfig,
):
    keys = [s.key for s in config.states]
    assert len(keys) == len(set(keys))
    assert config.open_states()
    assert any(s.terminal for s in config.states)


@PARAMS
def test_transitions_reference_declared_states(config: CaseTypeConfig):
    states = {s.key for s in config.states}
    for t in config.transitions:
        assert t.to_state in states, f"{t.key} -> unknown state {t.to_state}"
        assert set(t.from_states) <= states, f"{t.key} from unknown state"
        assert t.to_state not in t.from_states, f"{t.key} is a no-op"


@PARAMS
def test_transition_keys_are_unique_and_hold_a_real_permission(config: CaseTypeConfig):
    keys = [t.key for t in config.transitions]
    assert len(keys) == len(set(keys))
    for t in config.transitions:
        assert t.permission in set(Permission)


@PARAMS
def test_transitions_requiring_a_reason_code_declare_the_codes(config: CaseTypeConfig):
    for t in config.transitions:
        assert bool(t.reason_codes) == t.requires_reason_code, t.key
        code_keys = [r.key for r in t.reason_codes]
        assert len(code_keys) == len(set(code_keys)), t.key


@PARAMS
def test_four_eyes_controls_point_at_a_real_transition(config: CaseTypeConfig):
    keys = {t.key for t in config.transitions}
    for t in config.transitions:
        if t.distinct_actor_from:
            assert t.distinct_actor_from in keys, t.key


@PARAMS
def test_every_non_initial_state_is_reachable_and_can_be_left(config: CaseTypeConfig):
    reachable = {config.states[0].key} | {t.to_state for t in config.transitions}
    for state in config.states:
        assert state.key in reachable, f"{state.key} is unreachable"
        if not state.terminal:
            assert any(state.key in t.from_states for t in config.transitions), (
                f"{state.key} is a dead end but is not marked terminal"
            )


@PARAMS
def test_columns_are_renderable(config: CaseTypeConfig):
    for column in config.columns:
        assert column.type in COLUMN_TYPES, f"{column.key}: {column.type}"
        assert column.label
    assert sum(c.primary for c in config.columns) == 1


@PARAMS
def test_filters_declare_options_and_map_onto_the_queue_api(config: CaseTypeConfig):
    supported = {"q", "status", "priority", "assignee_id", "typology"}
    for f in config.filters:
        assert f.key in supported, f"no query parameter backs the '{f.key}' filter"
        if f.type == "select" and f.key != "assignee_id":
            assert f.options, f.key

    status_filter = next((f for f in config.filters if f.key == "status"), None)
    if status_filter:
        assert {o.value for o in status_filter.options} == {
            s.key for s in config.states
        }


@PARAMS
def test_presets_only_filter_on_declared_filters(config: CaseTypeConfig):
    filter_keys = {f.key for f in config.filters}
    for preset in config.presets:
        assert set(preset.filters) <= filter_keys, preset.key
        status = preset.filters.get("status")
        assert status is None or config.state(status), preset.key
    assert sum(p.default for p in config.presets) == 1


@PARAMS
def test_summary_and_column_keys_resolve_against_a_real_row(
    seeded_session, config: CaseTypeConfig
):
    """Header and column keys read either a row attribute or the case payload."""
    users = {u.id: u for u in seeded_session.exec(select(User)).all()}
    customers = {c.id: c for c in seeded_session.exec(select(Customer)).all()}
    cases = seeded_session.exec(select(Case).where(Case.case_type == config.key)).all()
    assert cases, f"no seed data for case type '{config.key}'"

    for case in cases:
        row = row_out(case, users, customers)
        for key in [f.key for f in config.summary_fields] + [
            c.key for c in config.columns
        ]:
            assert key in ROW_FIELDS or key in row.extra, (
                f"{config.key}: '{key}' resolves to nothing on {case.reference}"
            )


@PARAMS
def test_summary_fields_are_labelled(config: CaseTypeConfig):
    for field in config.summary_fields:
        assert field.label


@PARAMS
def test_evidence_tabs_declare_a_frontend_component(config: CaseTypeConfig):
    keys = [t.key for t in config.evidence_tabs]
    assert len(keys) == len(set(keys))
    for tab in config.evidence_tabs:
        assert tab.component and tab.component[0].isupper()


@PARAMS
def test_the_declaration_is_serialisable_over_the_api(client, users, config):
    response = client.get(
        f"/api/case-types/{config.key}", headers={"X-User-Id": users["admin"].id}
    )
    assert response.status_code == 200, response.text
    assert response.json()["key"] == config.key
