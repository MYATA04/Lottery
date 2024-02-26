from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from app.config_reader import config

# Создаем объект Bot
bot: Bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)

# Создаем объект Dispatcher (хэндлеры всеравно надо будет регистрировать в роутеры)
dp: Dispatcher = Dispatcher(storage=MemoryStorage())
