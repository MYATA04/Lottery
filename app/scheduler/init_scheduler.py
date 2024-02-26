from datetime import datetime, timedelta

import pytz
from app.logger import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Создаем объект планировщика задач, базой данных будет выступать SQLite (sqlalchemy)
scheduler = AsyncIOScheduler()
url = "sqlite:///database/example.sqlite"
scheduler.add_jobstore("sqlalchemy", url=url)


async def test_scheduler() -> None:
    logger.info("THE SCHEDULER STARTED SUCCESSFULLY!")


async def start_scheduler() -> None:
    """
    Проверка и старт планировщика задач
    """
    try:
        moscow_tz = pytz.timezone("Europe/Moscow")
        scheduler.start()

        run_date = datetime.now(tz=moscow_tz) + timedelta(seconds=0.5)
        scheduler.add_job(test_scheduler, "date", run_date=run_date)

    except TypeError as e:
        logger.exception(f"SCHEDULER IS NOT STARTED, SO PROCESS WILL BE STOPPED! {e}")
        raise
