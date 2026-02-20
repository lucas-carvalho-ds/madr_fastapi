import factory
import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from madr_fastapi.app import app
from madr_fastapi.database import enable_sqlite_foreign_keys, get_session
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


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    enable_sqlite_foreign_keys(engine)
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def user(session: Session) -> User:
    password = 'test123'

    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password  # type: ignore

    return user  # type: ignore


@pytest.fixture
def other_user(session: Session) -> User:
    password = 'test123'

    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password  # type: ignore

    return user  # type: ignore


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def novelist(session: Session) -> Novelist:
    novelist = NovelistFactory()

    session.add(novelist)
    session.commit()
    session.refresh(novelist)

    return novelist  # type: ignore


@pytest.fixture
def other_novelist(session: Session) -> Novelist:
    novelist = NovelistFactory()

    session.add(novelist)
    session.commit()
    session.refresh(novelist)

    return novelist  # type: ignore


@pytest.fixture
def book(session: Session, novelist: Novelist) -> Book:
    book = BookFactory(novelist_id=novelist.id)

    session.add(book)
    session.commit()
    session.refresh(book)

    return book  # type: ignore


@pytest.fixture
def other_book(session: Session, novelist: Novelist) -> Book:
    book = BookFactory(novelist_id=novelist.id)

    session.add(book)
    session.commit()
    session.refresh(book)

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
