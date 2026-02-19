from sqlalchemy import select

from madr_fastapi.models import User


def test_create_user(session):
    new_user = User(
        username='user_test', email='test123@gmail.com', password='test123'
    )

    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == 'user_test'))

    assert user.username == 'user_test'
