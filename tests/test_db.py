from sqlalchemy import select

from madr_fastapi.models import Account


def test_create_account(session):
    new_account = Account(
        username='account_test', email='test123@gmail.com', password='test123'
    )

    session.add(new_account)
    session.commit()

    account = session.scalar(
        select(Account).where(Account.username == 'account_test')
    )

    assert account.username == 'account_test'
