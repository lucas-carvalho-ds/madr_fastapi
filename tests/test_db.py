import pytest
from sqlalchemy import select

from madr_fastapi.models import Book, Novelist, User


@pytest.mark.asyncio
async def test_create_user(session):
    new_user = User(
        username='user_test', email='test123@gmail.com', password='test123'
    )

    session.add(new_user)
    await session.commit()

    user = await session.scalar(
        select(User).where(User.username == 'user_test')
    )

    assert user.username == 'user_test'


@pytest.mark.asyncio
async def test_create_novelist(session):
    new_novelist = Novelist(name='João da Silva')

    session.add(new_novelist)
    await session.commit()

    novelist = await session.scalar(
        select(Novelist).where(Novelist.name == 'João da Silva')
    )

    assert novelist.name == 'João da Silva'


@pytest.mark.asyncio
async def test_create_book(session, novelist):
    new_book = Book(
        title='Cavaleiro da Profecia', year=2026, novelist_id=novelist.id
    )

    session.add(new_book)
    await session.commit()

    book = await session.scalar(
        select(Book).where(Book.title == 'Cavaleiro da Profecia')
    )

    assert book.title == 'Cavaleiro da Profecia'
