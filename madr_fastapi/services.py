from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr_fastapi.models import User
from madr_fastapi.security import verify_password
from madr_fastapi.utils import sanitize_username


def verify_duplicate_user(session: Session, user) -> None:
    cleaned_username = sanitize_username(user.username)

    db_user = session.scalar(
        select(User).where(
            (User.username == cleaned_username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == cleaned_username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists.',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists.',
            )


def ensure_user_owner(current_user: User, user_id: int) -> None:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Unauthorized.',
        )


def authenticate_user(session: Session, email: str, password: str) -> User:

    user = session.scalar(select(User).where(User.email == email))

    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password.',
        )

    return user
