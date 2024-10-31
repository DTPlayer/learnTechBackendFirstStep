from fastapi import FastAPI

from api_router import router

from tortoise import Tortoise
from config import TORTOISE_CONFIG


async def lifecycle(app: FastAPI):
    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()

    yield

    await Tortoise.close_connections()

app = FastAPI(
    lifespan=lifecycle
)


app.mount('/api', router)
