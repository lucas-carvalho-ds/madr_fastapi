from http import HTTPStatus

from jwt import decode

from madr_fastapi.security import create_access_token


def test_jwt(settings):
    data = {'test': 'claim_value'}

    token = create_access_token(data)

    decoded_token = decode(
        token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
    )

    assert decoded_token['test'] == data['test']
    assert 'exp' in decoded_token


def test_jwt_invalid_token(client):
    response = client.delete(
        '/contas/conta/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials.'}


def test_get_current_account_not_found(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/contas/conta/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials.'}


def test_get_current_user_does_not_exists(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/contas/conta/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials.'}
