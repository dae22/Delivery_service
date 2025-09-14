from contextlib import asynccontextmanager

from fastapi import FastAPI

from delivery.database import async_session, engine
from delivery.logger import logger
from delivery.models import Base, init_package_type
from delivery.redis_client import close_redis, init_redis
from delivery.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Start app")
    await init_redis()

    logger.info("Redis initialized")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created")
    async with async_session() as session:
        await init_package_type(session)
        logger.info("Package types added")

    yield

    await close_redis()
    await engine.dispose()
    logger.info("Stop app")


app = FastAPI(lifespan=lifespan, title="Delivery Service")
app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Service is running"}
