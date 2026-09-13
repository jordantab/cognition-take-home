"""The case-type engine.

A case type is *declared*, not coded: states, transitions, queue columns,
filters, header fields and evidence tabs are data. The generic API serves that
declaration and the generic UI renders it. Adding an internal tool on top of
this platform means adding one module under `app/casetypes/` plus any genuinely
new evidence component.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core.rbac import Permission

Tone = str  # "neutral" | "info" | "warn" | "danger" | "success"


@dataclass(frozen=True)
class State:
    key: str
    label: str
    tone: Tone = "neutral"
    terminal: bool = False
    description: str = ""


@dataclass(frozen=True)
class ReasonCode:
    key: str
    label: str


@dataclass(frozen=True)
class Transition:
    key: str
    label: str
    from_states: tuple[str, ...]
    to_state: str
    permission: Permission
    variant: str = "default"  # button styling hint for the UI
    requires_note: bool = False
    requires_reason_code: bool = False
    reason_codes: tuple[ReasonCode, ...] = ()
    # Four-eyes: the actor must differ from whoever performed `distinct_from`.
    distinct_actor_from: str | None = None
    assigns_to_actor: bool = False
    description: str = ""


@dataclass(frozen=True)
class Column:
    key: str
    label: str
    type: str = "text"  # text|reference|money|date|age|risk|status|user|priority
    sortable: bool = False
    width: str | None = None
    primary: bool = False
    # Optional value -> tone map so `tag` columns carry semantic colour.
    tones: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class FilterOption:
    value: str
    label: str


@dataclass(frozen=True)
class Filter:
    key: str
    label: str
    type: str = "select"  # select|search|toggle
    options: tuple[FilterOption, ...] = ()
    placeholder: str = ""


@dataclass(frozen=True)
class SummaryField:
    key: str
    label: str
    type: str = "text"
    tones: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class EvidenceTab:
    key: str
    label: str
    component: str  # name resolved by the frontend evidence-component registry


@dataclass(frozen=True)
class QueuePreset:
    key: str
    label: str
    filters: dict[str, str] = field(default_factory=dict)
    mine: bool = False
    default: bool = False  # the view the queue opens on
    # Roles that open on this view instead of the default one, so an approver
    # does not land on an empty personal queue.
    default_for_roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class CaseTypeConfig:
    key: str
    label: str
    plural_label: str
    description: str
    icon: str
    reference_prefix: str
    sla_hours: int
    states: tuple[State, ...]
    transitions: tuple[Transition, ...]
    columns: tuple[Column, ...]
    filters: tuple[Filter, ...]
    summary_fields: tuple[SummaryField, ...]
    evidence_tabs: tuple[EvidenceTab, ...]
    presets: tuple[QueuePreset, ...]

    def state(self, key: str) -> State | None:
        return next((s for s in self.states if s.key == key), None)

    def transition(self, key: str) -> Transition | None:
        return next((t for t in self.transitions if t.key == key), None)

    def open_states(self) -> list[str]:
        return [s.key for s in self.states if not s.terminal]


_REGISTRY: dict[str, CaseTypeConfig] = {}


def register(config: CaseTypeConfig) -> CaseTypeConfig:
    _REGISTRY[config.key] = config
    return config


def get_case_type(key: str) -> CaseTypeConfig | None:
    return _REGISTRY.get(key)


def all_case_types() -> list[CaseTypeConfig]:
    return list(_REGISTRY.values())
