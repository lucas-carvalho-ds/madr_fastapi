from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from madr_fastapi.database import get_session
from madr_fastapi.models import User
from madr_fastapi.schemas import LoginToken
from madr_fastapi.security import (
    create_access_token,
    get_current_user,
)
from madr_fastapi.services import authenticate_user

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token', response_model=LoginToken)
async def login_for_access_token(
    form_data: OAuth2Form,
    session: SessionDep,
):
    user = await authenticate_user(
        session, form_data.username, form_data.password
    )

    access_token = create_access_token({'sub': user.email})

    return {'token_type': 'Bearer', 'access_token': access_token}


@router.post('/refresh_token', response_model=LoginToken)
async def refresh_access_token(user: CurrentUser):
    new_access_token = create_access_token({'sub': user.email})

    return {'token_type': 'Bearer', 'access_token': new_access_token}
