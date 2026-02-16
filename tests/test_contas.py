from http import HTTPStatus

from fastapi.testclient import TestClient

from madr_fastapi.app import app

client = TestClient(app)

