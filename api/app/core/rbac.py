"""Role and permission matrix for the case platform.

App-agnostic: case types declare which permission a transition requires, and the
matrix below decides which personas hold it.
"""

from enum import StrEnum


class Role(StrEnum):
    ANALYST = "analyst"
    SENIOR_ANALYST = "senior_analyst"
    COMPLIANCE_MANAGER = "compliance_manager"
    OPS_AGENT = "ops_agent"
    ADMIN = "admin"


ROLE_LABELS: dict[Role, str] = {
    Role.ANALYST: "Analyst",
    Role.SENIOR_ANALYST: "Senior Analyst",
    Role.COMPLIANCE_MANAGER: "Compliance Manager",
    Role.OPS_AGENT: "Ops Agent",
    Role.ADMIN: "Admin",
}


class Permission(StrEnum):
    CASE_VIEW = "case:view"
    CASE_COMMENT = "case:comment"
    CASE_CLAIM = "case:claim"
    CASE_ASSIGN_OTHERS = "case:assign_others"
    CASE_REQUEST_INFO = "case:request_info"
    CASE_CLOSE = "case:close"
    CASE_RECOMMEND = "case:recommend"
    CASE_APPROVE = "case:approve"
    CASE_REOPEN = "case:reopen"
    CASE_BULK = "case:bulk"
    CASE_EXPORT = "case:export"


_ANALYST = {
    Permission.CASE_VIEW,
    Permission.CASE_COMMENT,
    Permission.CASE_CLAIM,
    Permission.CASE_REQUEST_INFO,
    Permission.CASE_CLOSE,
    Permission.CASE_RECOMMEND,
    Permission.CASE_EXPORT,
}

_SENIOR_ANALYST = _ANALYST | {
    Permission.CASE_ASSIGN_OTHERS,
    Permission.CASE_BULK,
}

_COMPLIANCE_MANAGER = _SENIOR_ANALYST | {
    Permission.CASE_APPROVE,
    Permission.CASE_REOPEN,
}

PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ANALYST: _ANALYST,
    Role.SENIOR_ANALYST: _SENIOR_ANALYST,
    Role.COMPLIANCE_MANAGER: _COMPLIANCE_MANAGER,
    Role.OPS_AGENT: {Permission.CASE_VIEW, Permission.CASE_COMMENT},
    Role.ADMIN: set(Permission),
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in PERMISSIONS.get(role, set())


def permissions_for(role: Role) -> list[str]:
    return sorted(str(p) for p in PERMISSIONS.get(role, set()))
