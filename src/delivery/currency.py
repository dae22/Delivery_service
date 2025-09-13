import httpx
from sqlalchemy import select

import delivery.redis_client as redis_module
from delivery.database import async_session
from delivery.logger import logger
from delivery.models import PackagesDB

url = "https://www.cbr-xml-daily.ru/daily_json.js"


async def get_usd_rate():
    rate = await redis_module.redis_client.get("usd_rate")
    if not rate:
        logger.warning("Exchange rate is missing in Redis")
        return await update_usd_rate()
    return float(rate)


async def update_usd_rate():
    logger.info("Start update of exchange rate")
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    rate = data["Valute"]["USD"]["Value"]
    await redis_module.redis_client.set("usd_rate", rate, ex=24 * 3600)
    logger.info("Exchange rate updated in Redis")
    return float(rate)


async def calculate_delivery_prices():
    logger.info("Start calc func")
    usd_rate = await get_usd_rate()
    logger.info("USD rates received")

    async with async_session() as session:
        result = await session.execute(select(PackagesDB).where(PackagesDB.delivery_price.is_(None)))
        packages = result.scalars().all()

        if not packages:
            logger.info("There is no package for delivery price update")
            return

        for pkg in packages:
            pkg.delivery_price = (pkg.weight * 0.5 + pkg.price * 0.01) * usd_rate

        await session.commit()
        logger.info("Delivery price calculated")
