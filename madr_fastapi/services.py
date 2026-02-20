from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr_fastapi.models import Book, Novelist, User
from madr_fastapi.security import verify_password
from madr_fastapi.utils import sanitize_name


def verify_duplicate_user(session: Session, user) -> None:
    cleaned_username = sanitize_name(user.username)

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


def verify_duplicate_novelist(session: Session, novelist) -> None:
    cleaned_name = sanitize_name(novelist.name)

    db_novelist = session.scalar(
        select(Novelist).where((Novelist.name == cleaned_name))
    )

    if db_novelist:
        if db_novelist.name == cleaned_name:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Name already exists.',
            )


def get_novelist_or_return_404(session: Session, novelist_id: int) -> Novelist:
    db_novelist = session.scalar(
        select(Novelist).where(Novelist.id == novelist_id)
    )

    if not db_novelist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Novelist not found.'
        )

    return db_novelist


def verify_duplicate_book(session: Session, book) -> None:
    cleaned_title = sanitize_name(book.title)

    db_book = session.scalar(select(Book).where((Book.title == cleaned_title)))

    if db_book:
        if db_book.title == cleaned_title:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Title already exists.',
            )


def get_book_or_return_404(session: Session, book_id: int) -> Book:
    db_book = session.scalar(select(Book).where(Book.id == book_id))

    if not db_book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book not found.'
        )

    return db_book
