from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr_fastapi.models import Account
from madr_fastapi.security import verify_password
from madr_fastapi.utils import sanitize_username


def verify_duplicate_account(session: Session, account) -> None:
    cleaned_username = sanitize_username(account.username)

    db_account = session.scalar(
        select(Account).where(
            (Account.username == cleaned_username)
            | (Account.email == account.email)
        )
    )

    if db_account:
        if db_account.username == cleaned_username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists.',
            )
        elif db_account.email == account.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists.',
            )


def ensure_account_owner(current_account: Account, account_id: int) -> None:
    if current_account.id != account_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Unauthorized.',
        )


def authenticate_account(
    session: Session, email: str, password: str
) -> Account:

    account = session.scalar(select(Account).where(Account.email == email))

    if not account or not verify_password(password, account.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password.',
        )

    return account
