import asyncio
import contextlib
import os
from typing import Any

from aiogram import exceptions
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup
from app.config_reader import config
from app.database.bot_functions import delete_user_data, get_message_from_db, set_message_from_db
from app.dispatcher import bot
from app.logger import logger


async def get_message(name: str) -> dict | None:
    """
    Возваращет текст и картинку сообщения.

    На вход принимает:
        name - Название сообщения.

    Возвращает:
        Если сообщение с таким названием есть в базе данных, то возвращает словарь:
            {
                'text': text[0],
                'photo': text[1]
            }

        Если сообщение с таким названием нет в базе данных, то возвращает None:
            None
    """

    return await get_message_from_db(name)


async def set_message(name: str, text: str, photo: str = "") -> None:
    """
    Замена текста и картинки сообщения.

    На вход принимает:
        name - Название сообщения
        text - Текст сообщения
        photo - Картинка сообщения.

    Возвращает:
        Ничего не возвращает
    """
    await set_message_from_db(name, text, photo)


async def send_message_to_user(  # noqa: PLR0912, PLR0915, C901
    chat_id: int,
    name: str = None,
    text: str = None,
    photo_path: str = None,
    markup: InlineKeyboardMarkup | ReplyKeyboardMarkup = None,
    state: FSMContext = None,
    number: int = None,
) -> None:
    """
    Сложно структурная функция для отправки сообщения без ошибок и безопасно.

    На вход принимает:
        chat_id - Телеграм ID чата
        name - Название сообщения
        text - Текст сообщения (если сообщения с таким названием нет в базе данных или если название None)
        photo_path - Путь к картинке сообщения (если сообщения с таким названием нет в базе данных или если название None)
        markup - Клавиатура
        state - FSMContext объект, состояние для добавления message_id в нее для дальнейшего удаления из чата
        number - Номерок розыгрыша

    Возвращает:
        Ничего не возвращает
    """
    data = None

    if name is not None:  # Если название не None
        data = await get_message(name)  # То берем сообщение из базы данных

    if name is None or data is None:  # Если название None или такого сообщения нет в базе данных
        try:
            if photo_path is not None:  # Если в функцию был передан путь к картинке
                photo = FSInputFile(os.path.abspath(photo_path))  # noqa: PTH100  # Преоброзовываем в пригодный нам вид

                var = await bot.send_photo(chat_id=chat_id,
                                           photo=photo,
                                           caption=text,
                                           reply_markup=markup,
                                           protect_content=True)

                if name is not None:  # Если название не пустое
                    photo_id = var.photo[-1].file_id
                    text = var.md_text  # Берем текст с форматированием в markdown

                    await set_message(name=name, text=text, photo=photo_id)  # И сохроняем в базе данных

            else:  # Если в функцию не был передан путь к картинке
                var = await bot.send_message(chat_id=chat_id,
                                             text=text,
                                             reply_markup=markup,
                                             protect_content=True)

                if name is not None:  # Если название не пустое
                    text = var.md_text  # Берем текст с форматированием в markdown

                    await set_message(name=name, text=text, photo="")  # И сохроняем в базе данных

                    if name in ["winners_client", "losed_client"]:  # Если это сообщение для объявления результатов розыгрыша
                        text = f"<b><i>👆 Ваш номерок: {number}</i></b>"
                        
                        await bot.send_message(chat_id=chat_id,
                                               text=text,
                                               protect_content=True)  # Отправляем текст с номерком пользователя

        except exceptions.TelegramForbiddenError as e:  # Ошибка: пользователь ранее заблокировал бота
            logger.warning(
                f"Пользователь с ID - {chat_id} заблокировал бота, данный пользователь будет удален с базы данных: {e}"
            )
            await delete_user_data(user_id=chat_id)  # Удаляем пользователя из базы данных

            if state is not None:
                await state.clear()  # Очищаем данные пользователя из состояния

            return

    else:  # Если сообщение с таким названием есть в базе данных
        photo = data["photo"]
        text = data["text"]

        try:
            if photo:  # Если в сообщении есть ID картинки
                var = await bot.send_photo(chat_id=chat_id,
                                           photo=photo,
                                           caption=text,
                                           reply_markup=markup,
                                           parse_mode=ParseMode.MARKDOWN_V2,
                                           protect_content=True)

            else:  # Если в сообщении нет ID картинки
                var = await bot.send_message(chat_id=chat_id,
                                             text=text,
                                             reply_markup=markup,
                                             parse_mode=ParseMode.MARKDOWN_V2,
                                             protect_content=True)

            if name in ["winners_client", "losed_client"]:  # Если это сообщение для объявления результатов розыгрыша
                text = f"<b><i>👆 Ваш номерок: {number}</i></b>"
                
                await bot.send_message(chat_id=chat_id,
                                       text=text,
                                       protect_content=True)  # Отправляем текст с номерком пользователя

        except exceptions.TelegramBadRequest as e:  # Ошибка: не верный ID картинки для отправки
            logger.warning(f"ID картинки устарел, или оригинал был удален из чата, или ID картинки поменялся: {e}")
            await show_admins_warning_photo(name=name)  # Уведомляем админов, и говорим что картинка сообщения с таким названием устарел

            if photo_path is not None:  # Если в функцию был передан путь к картинке
                photo = FSInputFile(os.path.abspath(photo_path))  # noqa: PTH100

                var = await bot.send_photo(chat_id=chat_id,
                                           photo=photo,
                                           caption=text,
                                           reply_markup=markup,
                                           parse_mode=ParseMode.MARKDOWN_V2,
                                           protect_content=True)

                photo_id = var.photo[-1].file_id
                text = var.md_text  # Берем текст с форматированием в markdown

                await set_message(name=name, text=text, photo=photo_id)  # И сохроняем в базе данных

            else:  # Если в функцию не был передан путь к картинке
                var = await bot.send_message(chat_id=chat_id,
                                             text=text,
                                             reply_markup=markup,
                                             parse_mode=ParseMode.MARKDOWN_V2,
                                             protect_content=True)

                text = var.md_text  # Берем текст с форматированием в markdown

                await set_message(name=name, text=text, photo="")  # И сохроняем в базе данных

                if name in ["winners_client", "losed_client"]:  # Если это сообщение для объявления результатов розыгрыша
                    text = f"<b><i>👆 Ваш номерок: {number}</i></b>"

                    await bot.send_message(chat_id=chat_id,
                                           text=text,
                                           protect_content=True)  # Отправляем текст с номерком пользователя

        except exceptions.TelegramForbiddenError as e:  # Ошибка: пользователь ранее заблокировал бота
            logger.warning(
                f"Пользователь с ID - {chat_id} заблокировал бота, данный пользователь будет удален с базы данных: {e}"
            )
            await delete_user_data(user_id=chat_id)  # Удаляем пользователя из базы данных

            if state is not None:
                await state.clear()  # Очищаем данные пользователя из состояния

            return

    # Если в функцию было передано состояние и сообщения не об результатах розыгрыша
    if state is not None and name not in ["winners_client", "losed_client"]:
        # Добавляем message_id в состояние
        data = await state.get_data()
        message_ids = data.get("message_ids", [])
        message_ids.append(var.message_id)
        await state.update_data(message_ids=message_ids)


async def get_admins_show_text(name: str) -> str:
    """
    Создает текст для объявления всем админам бота, если при отправке сообщения пользователям появилась ошибка:

    exceptions.TelegramBadRequest: не верный ID картинки для отправки
    """
    format_text = name

    if name == "start_client":
        format_text = "Стартовое сообщение"
    elif name == "rules_client":
        format_text = "Сообщение правил"
    elif name == "admins_contacts_client":
        format_text = "Сообщение контактов"
    elif name == "winners_client":
        format_text = "Сообщение победителей"
    elif name == "losed_client":
        format_text = "Сообщение проигравших"
    elif name == "lottery_created_client":
        format_text = "Сообщение объявления розыгрыша"
    elif name == "request_adress":
        format_text = "Сообщение спроса адреса доставки"
    elif name == "response_adress":
        format_text = "Сообщение принятия адреса доставки"

    return (
        f'<b><i>ID картинки сообщения в: <i>"{format_text}"</i> устарел, или ID картинки поменялся, '
        "по этому картинка в этом случае будет базовым. Его можно изменить, отправив команду - /edit_text</i></b>"
    )


async def show_admins_warning_photo(name: str) -> None:
    """
    Если при отправке сообщения пользователям появилась ошибка:

    exceptions.TelegramBadRequest: не верный ID картинки для отправки;

    то объявляет всем админам об этом
    """
    text = await get_admins_show_text(name)  # Создаем текст для отправки

    for admin_id in config.ADMINS_IDS:  # Проходимся по каждому администратору
        with contextlib.suppress(exceptions.TelegramForbiddenError, exceptions.TelegramBadRequest):  # Игнорируем эти ошибки
            await bot.send_message(chat_id=admin_id, text=text)


async def delete_messages(state: FSMContext, chat_id: int) -> None:
    """
    Удаляет все сообщения в чате если message_id сообщения лежит в state
    """
    data = await state.get_data()
    message_ids = data.get("message_ids", [])  # Получаем список message_id-ев

    for message_id in message_ids:  # Проходимся по каждому message_id
        with contextlib.suppress(exceptions.TelegramBadRequest):  # Игнорируем эти ошибки
            await bot.delete_message(chat_id=chat_id, message_id=message_id)

    await state.update_data(message_ids=[])  # Опусташаем список message_id-ев


async def deleter(message: Message, state: FSMContext) -> None:
    """
    Функция в основном используется для главных команд бота в клиентской части, для остановления таймера, с удалением сообщении
    """
    await message.delete()
    await state.update_data(flag=2)

    await delete_messages(state=state, chat_id=message.from_user.id)


async def newsletter(
        chat_ids: list[[int | str, bool], Any] | list[int | str, bool],
        text: str,
        photo: str = ""
) -> bool:
    """
    Функция для рассылки или соло отправки сообщения пользователям бота которые находятся в базе данных
    """
    flag = False

    if isinstance(chat_ids[0], (str, int)):  # Если это соло отправка
        chat_ids = [chat_ids]
        flag = True

    for chat_id in chat_ids:  # Проходимся по каждому чату
        user_id = chat_id[0]    # Получаем user_id полльзователя
        user_flag = chat_id[1]  # Получаем разрешение на отправку пользователю

        if flag or user_flag:  # Если это соло отправка или пользователь давал разрешение на отправку ему рассылки
            try:
                if photo:  # Если в функцию была передана картинка
                    await bot.send_photo(chat_id=user_id,
                                         photo=photo,
                                         caption=text,
                                         parse_mode=ParseMode.MARKDOWN_V2)

                else:  # Если в функцию не была передана картинка
                    await bot.send_message(chat_id=user_id,
                                           text=text,
                                           parse_mode=ParseMode.MARKDOWN_V2)

            except exceptions.TelegramForbiddenError as e:  # noqa: PERF203  # Если пользователь ранее заблокировал бота
                logger.warning(
                    f"Пользователь с ID - {user_id} заблокировал бота, данный пользователь будет удален с "
                    f"базы данных: {e}"
                )
                await delete_user_data(user_id=user_id)  # Удаляем пользователя из базы данных

                if flag:  # Если это была соло отправка, возвращаем False
                    return False

            except exceptions.TelegramBadRequest as e:  # Если ID картинки не валидна
                logger.warning(
                    f"Рассылка остановилась. ID картинки устарел, или был удален оригинал из чата, или "
                    f"ID картинки поменялся: {e}"
                )
                text = (
                    "<i><b>Рассылка остановилась. ID картинки устарел, или был удален оригинал из чата, или ID "
                    "картинка поменялся.</b></i>"
                )

                for admin_id in config.ADMINS_IDS:  # Проходимся по каждому администратору
                    with contextlib.suppress(exceptions.TelegramForbiddenError, exceptions.TelegramBadRequest):  # Игнорируем эти ошибки
                        await bot.send_message(chat_id=admin_id, text=text)

                # То останавливаем рассылку
                return False

            except exceptions.TelegramRetryAfter as e:  # Если бот слишком часто отправляет сообщения
                logger.warning(f"Слишком высокая интенсивность отправки сообщении: {e}")
                sleep_time = int(e.retry_after) + 3
                await asyncio.sleep(sleep_time)  # То рассылка останавливается на некоторое время

    return True
