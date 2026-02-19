from http import HTTPStatus

from fastapi import FastAPI

from madr_fastapi.routers import auth, novelists, users

app = FastAPI(title='Projeto MADR')

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(novelists.router)


@app.get('/', status_code=HTTPStatus.OK)
def read_root():
    return {'message': 'Hello World!'}
