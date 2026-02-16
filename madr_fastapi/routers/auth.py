from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from madr_fastapi.database import get_session
from madr_fastapi.models import Account
from madr_fastapi.schemas import LoginToken
from madr_fastapi.security import (
    create_access_token,
    get_current_account,
)
from madr_fastapi.services import authenticate_account

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionDep = Annotated[Session, Depends(get_session)]
CurrentAccount = Annotated[Account, Depends(get_current_account)]


@router.post('/token', response_model=LoginToken)
def login_for_access_token(
    form_data: OAuth2Form,
    session: SessionDep,
):
    account = authenticate_account(
        session, form_data.username, form_data.password
    )

    access_token = create_access_token({'sub': account.email})

    return {'token_type': 'Bearer', 'access_token': access_token}


@router.post('/refresh_token', response_model=LoginToken)
def refresh_access_token(account: CurrentAccount):
    new_access_token = create_access_token({'sub': account.email})

    return {'token_type': 'Bearer', 'access_token': new_access_token}
