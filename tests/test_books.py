from http import HTTPStatus

import pytest

from madr_fastapi.schemas import BookPublic
from tests.conftest import BookFactory


def test_create_book(client, token, novelist):
    response = client.post(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'year': 2026,
            'title': 'O Rei Floreal',
            'novelist_id': novelist.id,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'year': 2026,
        'title': 'o rei floreal',
        'novelist_id': novelist.id,
    }


def test_update_integrity_error(client, book, other_book, token):
    response = client.patch(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': other_book.title},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Title already exists.'}


def test_list_books(client, book, token):
    books_schema = BookPublic.model_validate(book).model_dump(mode='json')

    response = client.get(
        '/books', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'books': [books_schema]}


def test_list_books_should_return_all_fields(client, token, book):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json()['books'] == [
        {
            'id': book.id,
            'year': book.year,
            'title': book.title,
            'novelist_id': book.novelist_id,
        }
    ]


@pytest.mark.asyncio
async def test_list_books_should_return_5_books(
    session, client, token, novelist
):
    expected_books = 5
    session.add_all(BookFactory.create_batch(5, novelist_id=novelist.id))
    await session.commit()

    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['books']) == expected_books


@pytest.mark.asyncio
async def test_list_books_pagination_should_return_2_books(
    session, client, token, novelist
):
    expected_books = 2
    session.add_all(BookFactory.create_batch(5, novelist_id=novelist.id))
    await session.commit()

    response = client.get(
        '/books/?page=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['books']) == expected_books


@pytest.mark.asyncio
async def test_list_books_filter_name_should_return_1_book(
    session, client, token, novelist
):
    expected_books = 1

    session.add(BookFactory.create(title='aaa', novelist_id=novelist.id))
    session.add(BookFactory.create(title='bab', novelist_id=novelist.id))
    session.add(BookFactory.create(title='ccc', novelist_id=novelist.id))
    await session.commit()

    response = client.get(
        '/books/?title=c',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['books']) == expected_books


@pytest.mark.asyncio
async def test_list_books_filter_year_should_return_3_books(
    session, client, token, novelist
):
    expected_books = 3

    session.add_all(
        BookFactory.create_batch(4, year=2018, novelist_id=novelist.id)
    )
    session.add_all(
        BookFactory.create_batch(3, year=2026, novelist_id=novelist.id)
    )
    session.add_all(
        BookFactory.create_batch(5, year=2023, novelist_id=novelist.id)
    )
    await session.commit()

    response = client.get(
        '/books/?year=2026', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['books']) == expected_books


def test_list_empty_books(client, token):
    response = client.get(
        '/books', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['books'] == []


def test_list_book(client, book, token):
    response = client.get(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'year': book.year,
        'title': book.title,
        'novelist_id': book.novelist_id,
    }


def test_not_found_list_book(client, token):
    response = client.get(
        '/books/0', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found.'}


def test_delete_book(client, book, token):
    response = client.delete(
        f'/books/{book.id}',  # type: ignore
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Book deleted successfully.'}


def test_not_found_delete_book(client, token):
    response = client.delete(
        '/books/0', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found.'}


def test_patch_book(client, book, token):
    response = client.patch(
        f'/books/{book.id}',
        json={'title': 'Cavaleiro da Luz'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'cavaleiro da luz'


def test_not_found_patch_book(client, token):
    response = client.patch(
        '/books/0',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found.'}


def test_novelist_not_found_patch_book(client, book, token):
    response = client.patch(
        f'/books/{book.id}',
        json={'novelist_id': 0},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Novelist not found.'}


def test_list_books_filter_min_length(client, token):
    tiny_string = ''
    response = client.get(
        f'/books/?title={tiny_string}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_list_books_filter_max_length(client, token):
    large_string = 'a' * 100
    response = client.get(
        f'/books/?title={large_string}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
