from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types.chat import Chat  # noqa: TCH002
from app.config_reader import config
from app.database.bot_functions import (
    add_user,
    check_user_in_db,
)


class UserInDbOrNot(BaseMiddleware):
    """
    Мидлварь, который чекает, есть ли такой пользователь в базе данных, и если его нет среди администраторов
    бота, то добавляет в базу данных.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Проверяем апдейт, если это например апдейт успешной оплаты, то пропускаем
        try:
            chat: Chat = data["event_chat"]  # chat object

        except KeyError:
            return await handler(event, data)

        chat_type = chat.type

        if chat_type != "private":  # Если тип чата не приватный, а например супергруппа, то не пропускаем
            return None

        user = data["event_from_user"]  # user object

        if user.id in config.ADMINS_IDS:  # Если Телеграм ID есть среди администраторов бота, то пропускаем
            return await handler(event, data)

        response: bool = await check_user_in_db(user.id)  # Если нет, то проверяем, есть ли пользователь в базе данных

        if not response:  # И если его там нет
            await add_user(user.id, user.username, user.full_name)  # То добавляем в базу данных

        return await handler(event, data)
