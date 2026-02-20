from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr_fastapi.database import get_session
from madr_fastapi.models import User
from madr_fastapi.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from madr_fastapi.security import get_current_user, get_password_hash
from madr_fastapi.services import (
    ensure_user_owner,
    verify_duplicate_user,
)
from madr_fastapi.utils import sanitize_name

router = APIRouter(prefix='/users', tags=['users'])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/user', response_model=UserPublic, status_code=HTTPStatus.CREATED
)
async def create_user(session: SessionDep, user: UserSchema):
    await verify_duplicate_user(session, user)

    cleaned_username = sanitize_name(user.username)

    db_user = User(
        username=cleaned_username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', response_model=UserList, status_code=HTTPStatus.OK)
async def list_users(session: SessionDep):
    users = await session.scalars(select(User))

    return {'users': users}


@router.put(
    '/user/{user_id}',
    response_model=UserPublic,
    status_code=HTTPStatus.OK,
)
async def update_user(
    session: SessionDep,
    current_user: CurrentUser,
    user_id: int,
    user: UserSchema,
):
    ensure_user_owner(current_user, user_id)

    try:
        cleaned_username = sanitize_name(user.username)

        current_user.username = cleaned_username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists.',
        )


@router.delete(
    '/user/{user_id}', response_model=Message, status_code=HTTPStatus.OK
)
async def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: int
):
    ensure_user_owner(current_user, user_id)

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted successfully.'}


@router.get(
    '/user/{user_id}',
    response_model=UserPublic,
    status_code=HTTPStatus.OK,
)
async def list_user(
    session: SessionDep, current_user: CurrentUser, user_id: int
):
    ensure_user_owner(current_user, user_id)

    db_user = await session.scalar(select(User).where(User.id == user_id))

    return db_user
