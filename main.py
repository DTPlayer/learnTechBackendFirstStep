from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api_router import router

from tortoise import Tortoise
from config import TORTOISE_CONFIG

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifecycle(app: FastAPI):
    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()

    yield

    print('Bye!')

app = FastAPI(
    lifespan=lifecycle
)


app.include_router(router, prefix='/api')


app.mount('/static', StaticFiles(directory='static'), name='static')
