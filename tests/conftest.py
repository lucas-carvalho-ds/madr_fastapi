import factory
import pytest
import pytest_asyncio
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from madr_fastapi.app import app
from madr_fastapi.database import get_session
from madr_fastapi.models import Book, Novelist, User, table_registry
from madr_fastapi.security import get_password_hash
from madr_fastapi.settings import Settings
from madr_fastapi.utils import sanitize_name


@pytest.fixture
def client(session):
    def get_session_overrides():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_overrides
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:latest', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def user(session: AsyncSession) -> User:
    password = 'test123'

    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password  # type: ignore

    return user  # type: ignore


@pytest_asyncio.fixture
async def other_user(session: AsyncSession) -> User:
    password = 'test123'

    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password  # type: ignore

    return user  # type: ignore


@pytest_asyncio.fixture
async def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest_asyncio.fixture
async def novelist(session: AsyncSession) -> Novelist:
    novelist = NovelistFactory()

    session.add(novelist)
    await session.commit()
    await session.refresh(novelist)

    return novelist  # type: ignore


@pytest_asyncio.fixture
async def other_novelist(session: AsyncSession) -> Novelist:
    novelist = NovelistFactory()

    session.add(novelist)
    await session.commit()
    await session.refresh(novelist)

    return novelist  # type: ignore


@pytest_asyncio.fixture
async def book(session: AsyncSession, novelist: Novelist) -> Book:
    book = BookFactory(novelist_id=novelist.id)

    session.add(book)
    await session.commit()
    await session.refresh(book)

    return book  # type: ignore


@pytest_asyncio.fixture
async def other_book(session: AsyncSession, novelist: Novelist) -> Book:
    book = BookFactory(novelist_id=novelist.id)

    session.add(book)
    await session.commit()
    await session.refresh(book)

    return book  # type: ignore


@pytest.fixture
def settings():
    return Settings()  # type: ignore


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@123')


class NovelistFactory(factory.Factory):
    class Meta:
        model = Novelist

    name = factory.LazyFunction(lambda: sanitize_name(Faker().name()))


class BookFactory(factory.Factory):
    class Meta:
        model = Book

    year = factory.LazyFunction(lambda: Faker().random_int(min=1900, max=2026))
    title = factory.LazyFunction(lambda: sanitize_name(Faker().word().title()))
    novelist_id = 1
