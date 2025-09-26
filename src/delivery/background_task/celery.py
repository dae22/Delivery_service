from celery import Celery
from celery.schedules import crontab

from delivery.settings import REDIS_URL

celery = Celery("delivery", broker=REDIS_URL, backend=REDIS_URL, include=["delivery.background_task.tasks"])

celery.conf.beat_schedule = {
    "update-rate-daily": {
        "task": "delivery.background_task.tasks.update_usd_rate",
        "schedule": crontab(minute=0, hour=7),
    },
    "calculate-price-5-minute": {
        "task": "delivery.background_task.tasks.calculate_delivery_prices",
        "schedule": 60.0,
    },
}
