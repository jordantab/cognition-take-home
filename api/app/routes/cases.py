from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.core.identity import CurrentUser, DbSession, require, to_user_out
from app.core.models import Case, User
from app.core.rbac import Permission
from app.core.schemas import (
    AssignRequest,
    CaseDetailOut,
    CaseListOut,
    CaseTypeOut,
    CommentOut,
    CommentRequest,
    MetricsOut,
    TransitionRequest,
)
from app.core.service import (
    add_comment,
    apply_transition,
    as_utc,
    assign_case,
    case_type_out,
    get_case_detail,
    list_cases,
    metrics,
)
from app.core.workflow import all_case_types, get_case_type

router = APIRouter(prefix="/api", tags=["cases"])


def _config(case_type: str):
    config = get_case_type(case_type)
    if config is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Unknown case type '{case_type}'."
        )
    return config


@router.get("/case-types", response_model=list[CaseTypeOut])
def read_case_types(session: DbSession) -> list[CaseTypeOut]:
    users = list(session.exec(select(User)).all())
    return [case_type_out(c, users) for c in all_case_types()]


@router.get("/case-types/{case_type}", response_model=CaseTypeOut)
def read_case_type(case_type: str, session: DbSession) -> CaseTypeOut:
    users = list(session.exec(select(User)).all())
    return case_type_out(_config(case_type), users)


@router.get("/case-types/{case_type}/cases", response_model=CaseListOut)
def read_cases(
    case_type: str,
    session: DbSession,
    current_user: CurrentUser,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    assignee_id: str | None = None,
    priority: str | None = None,
    typology: str | None = None,
    q: str | None = None,
    open_only: bool = False,
    sort: str = "due_at",
    direction: str = "asc",
    page: int = 1,
    page_size: int = 25,
) -> CaseListOut:
    return list_cases(
        session,
        _config(case_type),
        current_user,
        status_filter=status_filter,
        assignee_id=assignee_id,
        priority=priority,
        typology=typology,
        query=q,
        open_only=open_only,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )


@router.get("/case-types/{case_type}/metrics", response_model=MetricsOut)
def read_metrics(
    case_type: str, session: DbSession, current_user: CurrentUser
) -> MetricsOut:
    return metrics(session, _config(case_type), current_user)


def _load_case(session, case_id: str) -> Case:
    case = session.get(Case, case_id)
    if case is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found.")
    return case


@router.get("/cases/{case_id}", response_model=CaseDetailOut)
def read_case(
    case_id: str, session: DbSession, current_user: CurrentUser
) -> CaseDetailOut:
    case = _load_case(session, case_id)
    return get_case_detail(session, _config(case.case_type), case, current_user)


@router.post("/cases/{case_id}/transition", response_model=CaseDetailOut)
def post_transition(
    case_id: str,
    payload: TransitionRequest,
    session: DbSession,
    current_user: CurrentUser,
) -> CaseDetailOut:
    case = _load_case(session, case_id)
    config = _config(case.case_type)
    case = apply_transition(
        session,
        config,
        case,
        current_user,
        transition_key=payload.transition,
        note=payload.note,
        reason_code=payload.reason_code,
    )
    return get_case_detail(session, config, case, current_user)


@router.post("/cases/{case_id}/comments", response_model=CommentOut)
def post_comment(
    case_id: str,
    payload: CommentRequest,
    session: DbSession,
    current_user: CurrentUser,
) -> CommentOut:
    require(current_user, Permission.CASE_COMMENT)
    case = _load_case(session, case_id)
    comment = add_comment(session, case, current_user, payload.body)
    return CommentOut(
        id=comment.id,
        author=to_user_out(current_user),
        body=comment.body,
        created_at=as_utc(comment.created_at),
    )


@router.post("/cases/{case_id}/assignee", response_model=CaseDetailOut)
def post_assignee(
    case_id: str,
    payload: AssignRequest,
    session: DbSession,
    current_user: CurrentUser,
) -> CaseDetailOut:
    case = _load_case(session, case_id)
    if payload.assignee_id != current_user.id:
        require(current_user, Permission.CASE_ASSIGN_OTHERS)
    else:
        require(current_user, Permission.CASE_CLAIM)
    config = _config(case.case_type)
    case = assign_case(session, case, current_user, payload.assignee_id)
    return get_case_detail(session, config, case, current_user)
