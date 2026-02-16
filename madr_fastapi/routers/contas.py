from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter

from madr_fastapi.schemas import (
    AccountDB,
    AccountList,
    AccountPublic,
    AccountSchema,
    Message,
)

router = APIRouter(prefix='/contas', tags=['contas'])

database = []


@router.post(
    '/conta', response_model=AccountPublic, status_code=HTTPStatus.CREATED
)
def criar_conta(account: AccountSchema):
    account_db = AccountDB(
        id=len(database) + 1,
        username=account.username,
        email=account.email,
        password=account.password,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    database.append(account_db)

    return account_db


@router.get('/', response_model=AccountList, status_code=HTTPStatus.OK)
def listar_contas():
    return {'accounts': database}


@router.put(
    '/conta/{id}', response_model=AccountPublic, status_code=HTTPStatus.OK
)
def alterar_conta(account_id: int, account: AccountSchema):
    account_db = AccountDB(
        id=account_id,
        username=account.username,
        email=account.email,
        password=account.password,
        created_at=database[account_id].created_at,
        updated_at=datetime.now(),
    )

    database[account_id - 1] = account_db

    return account_db


@router.delete(
    '/conta/{id}', response_model=Message, status_code=HTTPStatus.OK
)
def deletar_conta(account_id: int):
    database.pop(account_id - 1)

    return {'message': 'Account deleted.'}
