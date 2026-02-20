from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from madr_fastapi.settings import Settings


def enable_sqlite_foreign_keys(engine):  # pragma: no cover
    if engine.url.get_backend_name() != 'sqlite':
        return

    @event.listens_for(engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


engine = create_engine(Settings().DATABASE_URL)  # type: ignore
enable_sqlite_foreign_keys(engine)


def get_session():  # pragma: no cover
    with Session(engine) as session:
        yield session
