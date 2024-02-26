from typing import Union, Any

import aiosqlite

from app.logger import logger


async def execute(query: str) -> None:
    """INSERT | UPDATE | DELETE"""
    async with aiosqlite.connect("database/bot_db.db") as conn:
        cur = await conn.cursor()

        try:
            await cur.execute(query)

        except aiosqlite.Error as e:
            logger.warning(f"[DATABASEERROR] execute - [{e}] - [query: {query}]")

            await conn.rollback()

        else:
            await conn.commit()


async def fetch_one_data(query: str) -> Union[str, int, False]:
    """SELECT (one element)"""
    async with aiosqlite.connect("database/bot_db.db") as conn:
        cur = await conn.cursor()

        try:
            await cur.execute(query)

        except aiosqlite.Error as e:
            logger.warning(f"[DATABASEERROR] fetch one - [{e}] - [query: {query}]")

            return None

        else:
            data = await cur.fetchone()

            if not data:
                return None

            return data[0]


async def fetch_one_row_data(query: str) -> list | None:
    """SELECT (one row)"""
    async with aiosqlite.connect("database/bot_db.db") as conn:
        cur = await conn.cursor()

        try:
            await cur.execute(query)

        except aiosqlite.Error as e:
            logger.warning(f"[DATABASEERROR] fetch row - [{e}] - [query: {query}]")

            return None

        else:
            data = await cur.fetchone()

            if not data:
                return None

            return list(data)


async def fetch_all_data(query: str) -> list[[str, Any], Any] | None:
    """SELECT (all)"""
    async with aiosqlite.connect("database/bot_db.db") as conn:
        cur = await conn.cursor()

        try:
            await cur.execute(query)

        except aiosqlite.Error as e:
            logger.warning(f"[DATABASEERROR] fetch all - [{e}] - [query: {query}]")

            return "ERROR"

        else:
            data = await cur.fetchall()

            if not data:
                return None

            return list(data)
