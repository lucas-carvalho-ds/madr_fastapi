from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, account):
    response = client.post(
        '/auth/token',
        data={'username': account.email, 'password': account.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK

    assert 'token_type' in token
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_login_inexistent_user(client):
    response = client.post(
        '/auth/token',
        data={'username': 'user_inexistent', 'password': 'inexistent123'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password.'}


def test_login_wrong_password(client, account):
    response = client.post(
        '/auth/token',
        data={'username': account.email, 'password': 'wrong_password'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password.'}


def test_token_expired_aftertime(client, account):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': account.email,
                'password': account.clean_password,
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 13:01:00'):
        response = client.put(
            f'/contas/conta/{account.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials.'}


def test_get_refresh_token(client, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    new_token = response.json()

    assert response.status_code == HTTPStatus.OK

    assert 'token_type' in new_token
    assert new_token['token_type'] == 'Bearer'
    assert 'access_token' in new_token


def test_token_expired_dont_refresh(client, account):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': account.email,
                'password': account.clean_password,
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 13:01:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials.'}
