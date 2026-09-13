from fastapi import APIRouter

from app.core.identity import CurrentUser, DbSession, to_user_out
from app.core.schemas import UserOut
from app.core.service import users_out

router = APIRouter(prefix="/api", tags=["identity"])


@router.get("/users", response_model=list[UserOut])
def read_users(session: DbSession) -> list[UserOut]:
    return users_out(session)


@router.get("/me", response_model=UserOut)
def read_me(current_user: CurrentUser) -> UserOut:
    return to_user_out(current_user)
