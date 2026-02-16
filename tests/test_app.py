from http import HTTPStatus

from fastapi.testclient import TestClient

from madr_fastapi.app import app

client = TestClient(app)


def test_should_return_status_code_200_and_hello_world():
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}
