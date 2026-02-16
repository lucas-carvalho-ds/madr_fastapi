from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from madr_fastapi.database import get_session
from madr_fastapi.models import Account
from madr_fastapi.schemas import (
    AccountList,
    AccountPublic,
    AccountSchema,
    Message,
)
from madr_fastapi.security import get_current_account, get_password_hash
from madr_fastapi.services import (
    ensure_account_owner,
    verify_duplicate_account,
)
from madr_fastapi.utils import sanitize_username

router = APIRouter(prefix='/contas', tags=['contas'])

SessionDep = Annotated[Session, Depends(get_session)]
CurrentAccount = Annotated[Account, Depends(get_current_account)]


@router.post(
    '/conta', response_model=AccountPublic, status_code=HTTPStatus.CREATED
)
def create_account(session: SessionDep, account: AccountSchema):
    verify_duplicate_account(session, account)

    cleaned_username = sanitize_username(account.username)

    db_account = Account(
        username=cleaned_username,
        email=account.email,
        password=get_password_hash(account.password),
    )

    session.add(db_account)
    session.commit()
    session.refresh(db_account)

    return db_account


@router.get('/', response_model=AccountList, status_code=HTTPStatus.OK)
def list_accounts(session: SessionDep):
    accounts = session.scalars(select(Account))

    return {'accounts': accounts}


@router.put(
    '/conta/{account_id}',
    response_model=AccountPublic,
    status_code=HTTPStatus.OK,
)
def update_account(
    session: SessionDep,
    current_account: CurrentAccount,
    account_id: int,
    account: AccountSchema,
):
    ensure_account_owner(current_account, account_id)

    try:
        cleaned_username = sanitize_username(account.username)

        current_account.username = cleaned_username
        current_account.email = account.email
        current_account.password = get_password_hash(account.password)

        session.add(current_account)
        session.commit()
        session.refresh(current_account)

        return current_account

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists.',
        )


@router.delete(
    '/conta/{account_id}', response_model=Message, status_code=HTTPStatus.OK
)
def delete_account(
    session: SessionDep, current_account: CurrentAccount, account_id: int
):
    ensure_account_owner(current_account, account_id)

    session.delete(current_account)
    session.commit()

    return {'message': 'Account deleted successfully.'}


@router.get(
    '/conta/{account_id}',
    response_model=AccountPublic,
    status_code=HTTPStatus.OK,
)
def list_account(
    session: SessionDep, current_account: CurrentAccount, account_id: int
):
    ensure_account_owner(current_account, account_id)

    db_account = session.scalar(
        select(Account).where(Account.id == account_id)
    )

    return db_account
