from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr_fastapi.database import get_session
from madr_fastapi.models import Novelist, User
from madr_fastapi.schemas import (
    Message,
    NovelistFilter,
    NovelistList,
    NovelistPublic,
    NovelistSchema,
    NovelistUpdate,
)
from madr_fastapi.security import get_current_user
from madr_fastapi.services import (
    get_novelist_or_return_404,
    verify_duplicate_novelist,
)
from madr_fastapi.utils import sanitize_name

router = APIRouter(prefix='/novelists', tags=['novelists'])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/novelist', response_model=NovelistPublic, status_code=HTTPStatus.CREATED
)
async def create_novelist(
    session: SessionDep, current_user: CurrentUser, novelist: NovelistSchema
):
    await verify_duplicate_novelist(session, novelist)

    cleaned_name = sanitize_name(novelist.name)

    db_novelist = Novelist(name=cleaned_name)

    session.add(db_novelist)
    await session.commit()
    await session.refresh(db_novelist)

    return db_novelist


@router.delete(
    '/novelist/{novelist_id}',
    response_model=Message,
    status_code=HTTPStatus.OK,
)
async def delete_novelist(
    session: SessionDep, current_user: CurrentUser, novelist_id: int
):
    db_novelist = await get_novelist_or_return_404(session, novelist_id)

    await session.delete(db_novelist)
    await session.commit()

    return {'message': 'Novelist deleted in MADR.'}


@router.patch(
    '/novelist/{novelist_id}',
    response_model=NovelistPublic,
    status_code=HTTPStatus.OK,
)
async def update_novelist(
    session: SessionDep,
    current_user: CurrentUser,
    novelist_id: int,
    novelist: NovelistUpdate,
):
    db_novelist = await get_novelist_or_return_404(session, novelist_id)
    await verify_duplicate_novelist(session, novelist)

    for key, value in novelist.model_dump(exclude_unset=True).items():
        new_value = value
        if key == 'name':
            new_value = sanitize_name(value)
        setattr(db_novelist, key, new_value)

    session.add(db_novelist)
    await session.commit()
    await session.refresh(db_novelist)

    return db_novelist


@router.get(
    '/novelist/{novelist_id}',
    response_model=NovelistPublic,
    status_code=HTTPStatus.OK,
)
async def list_novelist(
    session: SessionDep, current_user: CurrentUser, novelist_id: int
):
    db_novelist = await get_novelist_or_return_404(session, novelist_id)

    return db_novelist


@router.get('/', response_model=NovelistList, status_code=HTTPStatus.OK)
async def list_novelists(
    session: SessionDep,
    current_user: CurrentUser,
    novelist_filter: Annotated[NovelistFilter, Query()],
):
    query = select(Novelist)

    if novelist_filter.name:
        query = query.filter(Novelist.name.contains(novelist_filter.name))

    offset = (novelist_filter.page - 1) * novelist_filter.limit

    db_novelists = await session.scalars(
        query.offset(offset).limit(novelist_filter.limit)
    )

    return {'novelists': db_novelists.all()}
