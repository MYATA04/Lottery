from aiogram import Dispatcher
from app.handlers.client_handlers import check, commands_handlers, lottery


async def connect_client(dp: Dispatcher) -> None:
    """Регистрация роутеров хэндлеров клиентов бота"""
    dp.include_router(commands_handlers.router)
    dp.include_router(lottery.router)
    dp.include_router(check.router)
    # dp.include_router(request_address.router)
