from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import event

@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 1, 30)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)