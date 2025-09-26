import requests
from sqlalchemy import select

from delivery.background_task.celery import celery
from delivery.background_task.databace_sync import sync_session
from delivery.background_task.redis_client import redis_client
from delivery.logger import logger
from delivery.models import PackagesDB

url = "https://www.cbr-xml-daily.ru/daily_json.js"


def get_usd_rate():
    rate = redis_client.get("usd_rate")
    if not rate:
        logger.warning("Exchange rate is missing in Redis")
        return update_usd_rate()
    return float(rate)


@celery.task
def update_usd_rate():
    logger.info("Start update of exchange rate")
    response = requests.get(url)
    data = response.json()

    rate = data["Valute"]["USD"]["Value"]
    redis_client.set("usd_rate", rate, ex=24 * 3600)
    logger.info("Exchange rate updated in Redis")
    return float(rate)


@celery.task
def calculate_delivery_prices():
    logger.info("Start calc func")
    usd_rate = get_usd_rate()
    logger.info("USD rates received")

    with sync_session() as session:
        result = session.execute(select(PackagesDB).where(PackagesDB.delivery_price.is_(None)))
        packages = result.scalars().all()

        if not packages:
            logger.info("There is no package for delivery price update")
            return

        for pkg in packages:
            pkg.delivery_price = (pkg.weight * 0.5 + pkg.price * 0.01) * usd_rate

        session.commit()
        logger.info("Delivery price calculated")
