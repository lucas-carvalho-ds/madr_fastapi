from http import HTTPStatus

from madr_fastapi.schemas import AccountPublic


def test_create_account(client):
    response = client.post(
        '/contas/conta',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_read_accounts(client, account, token):
    account_schema = AccountPublic.model_validate(account).model_dump()

    response = client.get(
        '/contas', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'accounts': [account_schema]}


def test_update_account(client, account, token):
    response = client.put(
        f'/contas/conta/{account.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'alice nery',
            'email': 'alicenery@example.net',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'alice nery',
        'email': 'alicenery@example.net',
    }


def test_read_account(client, account, token):
    response = client.get(
        f'/contas/conta/{account.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': f'{account.username}',
        'email': f'{account.username}@test.com',
    }


def test_delete_account(client, account, token):
    response = client.delete(
        f'/contas/conta/{account.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Account deleted successfully.'}


def test_username_already_exists_create_account(client, account):
    response = client.post(
        '/contas/conta/',
        json={
            'username': account.username,
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists.'}


def test_email_already_exists_create_account(client, account):
    response = client.post(
        '/contas/conta/',
        json={
            'username': 'alice',
            'email': account.email,
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists.'}


def test_update_integrity_error(client, account, other_account, token):
    response = client.put(
        f'/contas/conta/{account.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_account.username,
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists.'}


def test_update_account_with_another_account(client, other_account, token):
    response = client.put(
        f'/contas/conta/{other_account.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Unauthorized.'}


def test_delete_account_with_another_account(client, other_account, token):
    response = client.delete(
        f'/contas/conta/{other_account.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Unauthorized.'}
