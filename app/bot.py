import asyncio
import sys

import errors
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope_chat import BotCommandScopeChat
from app.config_reader import config
from app.database.bot_functions import del_all_bookeds_from_lottery
from app.scheduler.functions import start_interval_lottery
from app.scheduler.init_scheduler import start_scheduler
from database import init_db
from dispatcher import bot, dp
from handlers import connect_admin, connect_client
from logger.loguru_logger import logger
from middlewares import LoggerMiddleware, UserInDbOrNot


async def main() -> None:
    # Инитиализируем базу данных
    await init_db()

    await del_all_bookeds_from_lottery()  # Убираем из базы данных все забронированные номерки

    logger.info("DATA BASE IS SUCCESSFUL CONNECTED!")

    # Пропускаем все апдейты когда бот был выключен
    await bot.delete_webhook(drop_pending_updates=True)

    # Добавляем меню команд в боте
    commands = [
        BotCommand(command="/help", description="Описания доступных команд"),
        BotCommand(command="/start", description="Вернуться в главное меню"),
        BotCommand(command="/edit_text", description="Изменить сообщения бота"),
        BotCommand(command="/statistics", description="Статистика активного розыгрыша"),
        BotCommand(command="/nlet_all", description="Массовая рассылка"),
        BotCommand(command="/nlet_one", description="Отправить сообщение пользователю"),
        BotCommand(command="/clet", description="Создать розыгрыш"),
        BotCommand(command="/get_logs", description="(для разработчиков) Журналы бота"),
    ]  # Эти команды для администраторов

    for admin_id in config.ADMINS_IDS:
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeChat(chat_id=admin_id))

    commands = [
        BotCommand(command="/start", description="Вернуться в главное меню"),
    ]  # Эти команды для клиентов

    await bot.set_my_commands(commands=commands)

    # Добавляем мидлвари
    dp.update.outer_middleware(UserInDbOrNot())
    dp.update.outer_middleware(LoggerMiddleware())

    logger.info("ALL MIDDLEWARES ARE CONNECTED!")

    # Добавляем роутера
    dp.include_routers(errors.router)

    await connect_admin(dp)
    await connect_client(dp)

    logger.info("ALL ROUTERS ARE CONNECTED!")

    logger.info("BOT IS STARTED!")

    # Запускаем планировщика задач
    await start_scheduler()
    await start_interval_lottery()

    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("BOT IS STOPPED!")
        sys.exit()

    except Exception:
        logger.critical("BOT IS STOPPED!")
        raise
