from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr_fastapi.database import get_session
from madr_fastapi.models import Book, User
from madr_fastapi.schemas import (
    BookFilter,
    BookList,
    BookPublic,
    BookSchema,
    BookUpdate,
    Message,
)
from madr_fastapi.security import get_current_user
from madr_fastapi.services import (
    get_book_or_return_404,
    get_novelist_or_return_404,
    verify_duplicate_book,
)
from madr_fastapi.utils import sanitize_name

router = APIRouter(prefix='/books', tags=['books'])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/', response_model=BookPublic, status_code=HTTPStatus.CREATED
)
async def create_book(
    session: SessionDep, current_user: CurrentUser, book: BookSchema
):
    await get_novelist_or_return_404(session, book.novelist_id)
    await verify_duplicate_book(session, book)

    cleaned_title = sanitize_name(book.title)

    db_book = Book(
        year=book.year, title=cleaned_title, novelist_id=book.novelist_id
    )

    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)

    return db_book


@router.delete(
    '/{book_id}', response_model=Message, status_code=HTTPStatus.OK
)
async def delete_book(
    session: SessionDep, current_user: CurrentUser, book_id: int
):
    db_book = await get_book_or_return_404(session, book_id)

    await session.delete(db_book)
    await session.commit()

    return {'message': 'Book deleted successfully.'}


@router.patch(
    '/{book_id}', response_model=BookPublic, status_code=HTTPStatus.OK
)
async def update_book(
    session: SessionDep,
    current_user: CurrentUser,
    book_id: int,
    book: BookUpdate,
):
    db_book = await get_book_or_return_404(session, book_id)
    if book.novelist_id is not None:
        await get_novelist_or_return_404(session, book.novelist_id)
    await verify_duplicate_book(session, book)

    for key, value in book.model_dump(exclude_unset=True).items():
        new_value = value
        if key == 'title':
            new_value = sanitize_name(value)
        setattr(db_book, key, new_value)

    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)

    return db_book


@router.get(
    '/{book_id}', response_model=BookPublic, status_code=HTTPStatus.OK
)
async def list_book(
    session: SessionDep, current_user: CurrentUser, book_id: int
):
    db_book = await get_book_or_return_404(session, book_id)

    return db_book


@router.get('/', response_model=BookList, status_code=HTTPStatus.OK)
async def list_books(
    session: SessionDep,
    current_user: CurrentUser,
    book_filter: Annotated[BookFilter, Query()],
):
    query = select(Book)

    if book_filter.title:
        query = query.filter(Book.title.contains(book_filter.title))

    if book_filter.year:
        query = query.filter(Book.year == book_filter.year)

    offset = (book_filter.page - 1) * book_filter.limit

    db_books = await session.scalars(
        query.offset(offset).limit(book_filter.limit)
    )

    return {'books': db_books.all()}
