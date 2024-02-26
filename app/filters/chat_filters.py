from typing import Union

from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message
from app.config_reader import config


class IsAdmin(Filter):
    """Фильтр только для администраторов бота"""

    def __init__(self) -> None:
        pass

    async def __call__(self, query_or_message: Union[Message, CallbackQuery]) -> bool:
        return query_or_message.from_user.id in config.ADMINS_IDS


class IsClient(Filter):
    """Фильтр только для клиентов бота"""

    def __init__(self) -> None:
        pass

    async def __call__(self, query_or_message: Union[Message, CallbackQuery]) -> bool:
        return query_or_message.from_user.id not in config.ADMINS_IDS
