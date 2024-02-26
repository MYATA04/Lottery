from aiogram import Dispatcher
from app.handlers.admin_handlers import commands_handlers, create_lottery, edit_texts, newsletter


async def connect_admin(dp: Dispatcher) -> None:
    """Регистрация роутеров хэндлеров администраторов бота"""
    dp.include_router(commands_handlers.router)
    dp.include_router(edit_texts.router)
    dp.include_router(newsletter.router)
    dp.include_router(create_lottery.router)
