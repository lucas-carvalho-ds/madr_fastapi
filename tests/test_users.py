from http import HTTPStatus

from madr_fastapi.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/users/user',
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


def test_read_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/user/{user.id}',
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


def test_read_user(client, user, token):
    response = client.get(
        f'/users/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': f'{user.username}',
        'email': f'{user.username}@test.com',
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully.'}


def test_username_already_exists_create_user(client, user):
    response = client.post(
        '/users/user/',
        json={
            'username': user.username,
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists.'}


def test_email_already_exists_create_user(client, user):
    response = client.post(
        '/users/user/',
        json={
            'username': 'alice',
            'email': user.email,
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists.'}


def test_update_integrity_error(client, user, other_user, token):
    response = client.put(
        f'/users/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists.'}


def test_update_user_with_another_user(client, other_user, token):
    response = client.put(
        f'/users/user/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Unauthorized.'}


def test_delete_user_with_another_user(client, other_user, token):
    response = client.delete(
        f'/users/user/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Unauthorized.'}
