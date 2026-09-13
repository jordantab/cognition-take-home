"""Mocked identity.

The demo has no real IdP: the caller asserts who they are with an `X-User-Id`
header and the platform resolves their role and permissions from the database.
Swapping this dependency for a real OIDC token is the only change needed to make
the RBAC below production-shaped.
"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

from app.core.models import User
from app.core.rbac import ROLE_LABELS, Permission, Role, has_permission, permissions_for
from app.core.schemas import UserOut
from app.db import get_session


def initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    return "".join(p[0].upper() for p in parts[:2])


def to_user_out(user: User) -> UserOut:
    role = Role(user.role)
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        role_label=ROLE_LABELS[role],
        job_title=user.job_title,
        team=user.team,
        initials=initials(user.name),
        permissions=permissions_for(role),
    )


def get_current_user(
    session: Annotated[Session, Depends(get_session)],
    x_user_id: Annotated[str | None, Header()] = None,
) -> User:
    statement = select(User)
    if x_user_id:
        statement = statement.where(User.id == x_user_id)
    user = session.exec(statement.order_by(User.id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown user. Pick a persona with the X-User-Id header.",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_session)]


def require(user: User, permission: Permission) -> None:
    if not has_permission(Role(user.role), permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{ROLE_LABELS[Role(user.role)]} cannot perform {permission}.",
        )
