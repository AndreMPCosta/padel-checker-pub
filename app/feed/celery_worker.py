from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta
from os import environ, cpu_count

from celery import Celery
from celery.utils.log import get_task_logger

# Initialize celery
from app.feed.config import cities
from app.feed.fetcher import Zone

celery = Celery('tasks', broker=f'amqp://{environ.get("RABBITMQ_USER")}:{environ.get("RABBITMQ_PASSWORD")}'
                                f'@localhost:5672', backend='rpc://')
# Create logger - enable to display messages on task logger
celery_log = get_task_logger(__name__)

celery.conf.timezone = 'Europe/Lisbon'


@celery.task
def cycle_days():
    processes = []
    zones = []
    base = datetime.today()
    date_list = [(base + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(7)]
    all_ids = [x for x in cities.values()]
    for _id in all_ids:
        zones += [Zone(internal_date=date, id=_id) for date in date_list]
    # zones = [Zone(internal_date=date) for date in date_list]

    with ThreadPoolExecutor(max_workers=min(32, (cpu_count() or 1) + 4)) as executor:
        for zone in zones:
            processes.append(executor.submit(refresh_data, zone))

    return {"message": "Refresh successful"}


@celery.task
def internal_refresh(z):
    refresh_data(z)


# Pull data from API - Run Asynchronously with celery
def refresh_data(z):
    z.get_all_courts()
    z.court_list.build_clubs()
    city_name = next(key for key, value in cities.items() if value == z.id)
    celery_log.info(f"Refresh Complete for zone {city_name} - {z.internal_date}")
