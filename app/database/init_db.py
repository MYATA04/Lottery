import sys

import aiosqlite
from aiosqlite import Cursor
from app.database.database_functions import execute, fetch_one_row_data
from app.logger import logger


async def init_db() -> None:
    """
    Создает таблицы в базе данных.

    Таблицы:
        user -> id, username, fullname, notification, numbers, phone
        texts -> name, text, photo
        lottery -> id, text, photo, numbers_amount, purchased, price, booked, win_numbers_amount, date, flag
    """
    try:
        async with aiosqlite.connect("database/bot_db.db") as conn:
            cur: Cursor = await conn.cursor()

            await cur.execute(
                """
                              CREATE TABLE IF NOT EXISTS user(
                                  id VARCHAR(12) PRIMARY KEY,
                                  username VARCHAR(32),
                                  fullname TEXT,
                                  notification VARCHAR(1),
                                  numbers TEXT,
                                  phone TEXT
                              )
                              """
            )

            await cur.execute(
                """
                              CREATE TABLE IF NOT EXISTS texts(
                                  name VARCHAR(20) PRIMARY KEY,
                                  text TEXT,
                                  photo TEXT
                              )
                              """
            )

            await cur.execute(
                """
                              CREATE TABLE IF NOT EXISTS lottery(
                                  id VARCHAR(1) PRIMARY KEY,
                                  text TEXT,
                                  photo TEXT,
                                  numbers_amount TEXT,
                                  purchased TEXT,
                                  price TEXT,
                                  booked TEXT,
                                  win_numbers_amount TEXT,
                                  date TEXT,
                                  flag VARCHAR(1)
                              )
                              """
            )

            check = await fetch_one_row_data("SELECT * FROM lottery WHERE id = '1'")  # Проверяем, есть ли уже созданный ранее розыгрыш

            if check is None:  # Если нет, то создаем его, дав флаг 0, то есть, сделва его сразу не активным
                await execute("INSERT INTO lottery(id, flag) VALUES ('1', '0')")

            await conn.commit()

    except aiosqlite.Error as e:
        logger.exception(f"DATA BASE IS NOT CONNECTED, SO PROCESS WILL BE STOPPED!\nError: {e}")
        sys.exit()
