from http import HTTPStatus

import pytest

from madr_fastapi.schemas import NovelistPublic
from tests.conftest import NovelistFactory


def test_create_novelist(client, token):
    response = client.post(
        '/novelists',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'Mario Brás'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'id': 1, 'name': 'mario brás'}


def test_update_integrity_error(client, novelist, other_novelist, token):
    response = client.patch(
        f'/novelists/{novelist.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': other_novelist.name},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Name already exists.'}


def test_list_novelists(client, novelist, token):
    novelists_schema = NovelistPublic.model_validate(novelist).model_dump(
        mode='json'
    )

    response = client.get(
        '/novelists', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'novelists': [novelists_schema]}


def test_list_novelists_should_return_all_fields(client, token, novelist):
    response = client.get(
        '/novelists',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json()['novelists'] == [
        {'id': novelist.id, 'name': novelist.name}
    ]


@pytest.mark.asyncio
async def test_list_novelists_should_return_5_novelists(
    session, client, token
):
    expected_novelists = 5
    session.add_all(NovelistFactory.create_batch(5))
    await session.commit()

    response = client.get(
        '/novelists',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['novelists']) == expected_novelists


@pytest.mark.asyncio
async def test_list_novelists_pagination_should_return_2_novelists(
    session, client, token
):
    expected_novelists = 2
    session.add_all(NovelistFactory.create_batch(5))
    await session.commit()

    response = client.get(
        '/novelists/?page=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['novelists']) == expected_novelists


@pytest.mark.asyncio
async def test_list_novelists_filter_name_should_return_5_novelists(
    session, client, token
):
    expected_novelists = 1

    session.add(NovelistFactory.create(name='aaa'))
    session.add(NovelistFactory.create(name='bab'))
    session.add(NovelistFactory.create(name='ccc'))
    await session.commit()

    response = client.get(
        '/novelists/?name=c',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['novelists']) == expected_novelists


def test_list_empty_novelists(client, token):
    response = client.get(
        '/novelists', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['novelists'] == []


def test_list_novelist(client, novelist, token):
    response = client.get(
        f'/novelists/{novelist.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'name': novelist.name}


def test_not_found_list_novelist(client, token):
    response = client.get(
        '/novelists/0', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Novelist not found.'}


def test_delete_novelist(client, novelist, token):
    response = client.delete(
        f'/novelists/{novelist.id}',  # type: ignore
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Novelist deleted in MADR.'}


def test_not_found_delete_novelist(client, token):
    response = client.delete(
        '/novelists/0', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Novelist not found.'}


def test_patch_novelist(client, novelist, token):
    response = client.patch(
        f'/novelists/{novelist.id}',
        json={'name': 'João de Lima'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == 'joão de lima'


def test_not_found_patch_novelist(client, token):
    response = client.patch(
        '/novelists/0',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Novelist not found.'}


def test_list_novelists_filter_min_length(client, token):
    tiny_string = ''
    response = client.get(
        f'/novelists/?name={tiny_string}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_list_novelists_filter_max_length(client, token):
    large_string = 'a' * 100
    response = client.get(
        f'/novelists/?name={large_string}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
