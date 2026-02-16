from http import HTTPStatus

from fastapi import FastAPI

from madr_fastapi.routers import contas

app = FastAPI(title='Projeto MADR')

app.include_router(contas.router)


@app.get('/', status_code=HTTPStatus.OK)
def read_root():
    return {'message': 'Hello World!'}
