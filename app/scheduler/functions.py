import asyncio
import contextlib
from random import randint

from aiogram import exceptions
from app.config_reader import config
from app.database.bot_functions import (
    check_lottery,
    close_lottery,
    get_data_lottery,
    get_user,
    get_users_ids_and_numbers_who_player_lottery,
)
from app.dispatcher import bot
from app.keyboards.client_kb import IKB
from app.logger import logger
from app.scheduler.init_scheduler import scheduler
from app.texts.functions import send_message_to_user
from app.texts.texts import CLIENTS_TEXTS


async def start_interval_lottery() -> None:
    """Задача, которая запускает функцию для проверки результатов розыгрыша каждые 2 часа"""
    if scheduler.get_job("lottery"):
        scheduler.remove_job(job_id="lottery")

    logger.info("[SCHEDULER] Запущена новая задача для проверки результатов розыгрыша")

    scheduler.add_job(checker_lottery_result, "interval", hours=2, id="lottery")  # Каждые 2 часа проверяем результаты розыгрыша


async def checker_lottery_result() -> None:  # noqa: C901
    """Функция для проверки результатов розыгрыша"""
    check = await check_lottery()
    config.reload_objects()

    if not check:  # Если на данный момент розыгрыш не идет, то просто скипаем, и дальше не идем
        return

    data = await get_data_lottery()
    numbers_amount = int(data["numbers_amount"])  # Количество номерков
    purchased = data["purchased"].split(",")      # Купленные номерки

    if numbers_amount == len(purchased):
        logger.info("[SCHEDULER] Все номерки куплены, сейчас будут объявлены результаты розыгрыша . . .")

        await asyncio.sleep(10)

        win_numbers_amount = int(data["win_numbers_amount"])  # Количество победных номерков
        win_numbers = []

        while len(win_numbers) != win_numbers_amount:  # Выбираем рандомно победные номерки
            number = randint(1, numbers_amount)

            if number not in win_numbers:
                win_numbers.append(number)

        text_lottery = data["text"]    # Текст розыгрыша
        photo_lottery = data["photo"]  # Картинка розыгрыша
        price = data["price"]          # Цена одного номерка
        date = data["date"]            # Дата создания розыгрыша

        users = await get_users_ids_and_numbers_who_player_lottery()  # Все ID-шники и номерки участвовавших в данном розыгрыше

        # Создаем им сообщения для отправки
        winners_name = "winners_client"
        text_winners = CLIENTS_TEXTS[winners_name]
        winners_list = []

        losed_name = "losed_client"
        text_losed = CLIENTS_TEXTS[losed_name]

        for user in users:
            user_id = user[0]
            user_numbers = user[1]
            await bot.send_photo(chat_id=user_id, photo=photo_lottery, caption=text_lottery)  # Отправляем данные розыгрыша

            for number in user_numbers:  # И проходимся по каждому номерку участника
                if number in win_numbers:
                    await send_message_to_user(chat_id=user_id,
                                               name=winners_name,
                                               text=text_winners,
                                               markup=await IKB.request_address(number=number),
                                               number=number)

                    winners_list.append([user_id, number])

                else:
                    await send_message_to_user(chat_id=user_id,
                                               name=losed_name,
                                               text=text_losed,
                                               number=number)

        # Дальше уже уведомляем администраторов
        text = f"<i><b>Цена одного номерка: {price} ₽\nДата создания розыгрыша: {date}\nПобедители розыгрыша:\n"

        for winner in winners_list:
            user_number = winner[1]
            user_id = winner[0]
            user_db = await get_user(user_id)
            user_numbers = " | ".join(user_db["numbers"].split(","))

            try:
                user = await bot.get_chat(user_id)

                text += (f"\nНомерок: <u>{user_number}</u>\nID пользователя: <code>{user.id}</code>\nПолное имя: "
                         f"<code>{user.full_name}</code>\n"
                         f"UserName пользователя: <code>{user.username}</code>\nНомерки пользователя: "
                         f"<code>{user_numbers}</code>\n")

            except exceptions.TelegramForbiddenError:  # noqa: PERF203
                text += (f"\nНомерок: <u>{user_number}</u>\nID пользователя: <code>{user_db["id"]}</code>\nПолное имя: "
                         f"<code>{user_db["full_name"]}"
                         f"</code>\nUserName пользователя: <code>{user_db["username"]}</code>\nНомерки пользователя: "
                         f"<code>{user_numbers}</code>\n<u>Данный пользователь "
                         f"ранее заблокировал бота</u>\n")

        text += "</b></i>"
        text_2 = ('<i>Вы можете отправить им личное сообщение по отправке текстовой команды - '
                  '"<code>🏷 Отправка пользователю</code>" или обычной командой - /nlet_one</i>')

        for admin_id in config.ADMINS_IDS:
            with contextlib.suppress(exceptions.TelegramForbiddenError, exceptions.TelegramBadRequest):
                await bot.send_photo(chat_id=admin_id, photo=photo_lottery, caption=text_lottery)  # Данные розыгрыша
                await bot.send_message(chat_id=admin_id, text=text)                                # Данные победителей
                await bot.send_message(chat_id=admin_id, text=text_2)                              # Совет связки с клиентом

        await close_lottery()                   # Закрываем розыгрыш
        scheduler.remove_job(job_id="lottery")  # Удаляем данную задачу

        logger.info("[SCHEDULER] Результаты розыгрыша были объявлены, закрываем розыгрыш и убираем задачу на проверку результатов розыгрыша")

    else:
        logger.info("[SCHEDULER] Еще не все номерки куплены, по этому результаты розыгрыша пока не будут объявлены")
