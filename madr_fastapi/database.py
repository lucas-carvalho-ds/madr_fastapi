from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from madr_fastapi.settings import Settings


def enable_sqlite_foreign_keys(engine):  # pragma: no cover
    if engine.url.get_backend_name() != 'sqlite':
        return

    @event.listens_for(engine.sync_engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


engine = create_async_engine(Settings().DATABASE_URL)  # type: ignore

enable_sqlite_foreign_keys(engine)


async def get_session():  # pragma: no cover
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
