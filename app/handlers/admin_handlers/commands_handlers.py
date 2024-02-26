import os
from datetime import datetime

import pytz
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from app.database.bot_functions import check_lottery, get_all_users_ids, get_data_lottery, get_all_users
from app.filters import IsAdmin
from app.fsm import FSMAdmin
from app.keyboards.admin_kb import RKB
from app.texts.functions import get_message, set_message

router = Router()


@router.message(CommandStart(), IsAdmin())
@router.message(F.text.in_(["🔖 Перейти в главное меню", "Отменить изменение"]), IsAdmin())
async def command_start_handling(message: Message, state: FSMContext) -> None:
    await message.delete()

    await state.set_state(FSMAdmin.passive)

    text = f"👋 Добро пожаловать - {message.from_user.full_name} 🟡 🟢 🔴 ⚪️\n\n🗂 Вам доступны следующие команды:"
    name = "start_admin"
    photo_path = "medias/start_admin.png"
    markup = await RKB.main_commands()

    data = await get_message(name)

    if data is None:
        photo = FSInputFile(os.path.abspath(photo_path))  # noqa: PTH100
        var = await message.answer_photo(photo=photo, caption=text, reply_markup=markup)
        photo_id = var.photo[-1].file_id

        await set_message(name=name, text="", photo=photo_id)

    else:
        photo = data["photo"]

        await message.answer_photo(photo=photo, caption=text, reply_markup=markup)


@router.message(Command("help"), IsAdmin())
@router.message(F.text == "🆘 Помощь по командам", IsAdmin())
async def command_help_handling(message: Message, state: FSMContext) -> None:
    await message.delete()

    await state.set_state(FSMAdmin.passive)

    text = f"👋 Добро пожаловать - {message.from_user.full_name} 🟡 🟢 🔴 ⚪️\n\n🗂 Вам доступны следующие команды:\n\n"
    name = "help_admin"
    photo_path = "medias/help_admin.png"
    markup = await RKB.main_commands()

    data = await get_message(name)

    if data is None:
        photo = FSInputFile(os.path.abspath(photo_path))  # noqa: PTH100
        var = await message.answer_photo(photo=photo, caption=text, reply_markup=markup)
        photo_id = var.photo[-1].file_id

        await set_message(name=name, text="", photo=photo_id)

    else:
        photo = data["photo"]

        await message.answer_photo(photo=photo, caption=text, reply_markup=markup)

    text = (
        ".    <code>🎉 Создать розыгрыш</code> - создать новый розыгрыш, бот попросит у вас сперва картинку товара, "
        "после текст, форматированный или без, после количество номерков, после цену номерка, после "
        "количество победителей, после подтвердить создание розыгрыша. Этот розыгрыш автоматически отправится "
        "всем пользователем бота, если он даже админ. Выигрышные номерки выберутся автоматически, и после "
        "конца всех номерков, бот автоматически уведомит победителей, а проигравшим пожелает удачи, а админам "
        "отправит ID победителей, их @username, их полное имя в телеграме. После, "
        "бот у победителей попросит адрес, получив его, отправит всем админам бота, вместе с ID, @username, "
        "полным именем.\n\n"
        "      <code>📝 Изменить текста бота</code> - изменить доступные к изменению текста бота, как например, "
        "приветственное сообщение клиентов (/start команда), помощь по командам (/help), сообщение при "
        "объявлений победителей розыгрыша победителям, проигравшим. Доступные к изменению текста можно "
        'посмотреть отправив команду /set_text или нажав на команду снизу - "📝 Изменить текста бота".\n\n'
        "      <code>✉️ Массовая рассылка</code> - рассылка всем пользователям бота, с картинкой или без.\n\n"
        "      <code>🏷 Отправка пользователю</code> - рассылка конкретному пользователю, с картинкой или без, "
        "отправив боту ID пользователя.\n\n"
        "      <code>🗃 Статистика</code> - просмотр количество пользователей бота и данные активного розыгрыша.\n\n"
    )

    await message.answer(text=text)


@router.message(Command("get_logs"), IsAdmin())
async def command_get_logs_handling(message: Message, state: FSMContext) -> None:
    await message.delete()

    await state.set_state(FSMAdmin.passive)

    path = os.path.abspath("logger/logs/")  # noqa: PTH100

    list_ = os.listdir(path)

    for file in list_:
        document = FSInputFile(path + "\\" + file, filename=file[:-3] + ".log")
        await message.answer_document(document=document)

    path = os.path.abspath("database/bot_db.db")  # noqa: PTH100
    moscow_tz = pytz.timezone("Europe/Moscow")
    date = datetime.now(tz=moscow_tz).strftime("%d_%m_%Y")
    document = FSInputFile(path, filename=f"{date}.db")
    await message.answer_document(document=document)


@router.message(Command("statistics"), IsAdmin())
@router.message(F.text == "🗃 Статистика", IsAdmin())
async def command_statistics_handling(message: Message, state: FSMContext) -> None:
    await message.delete()

    await state.set_state(FSMAdmin.passive)

    users_count = len(await get_all_users_ids())

    if users_count == 0:
        text = "<b>На данный момент в базе данных нет пользователей ⚪️</b>\n\n"

    else:
        text = f"Количество пользователей бота: <i>{users_count}</i>\n\n"

    check = await check_lottery()

    if check:
        data = await get_data_lottery()
        photo = data["photo"]
        text_lottery = data["text"]
        text += (
            f"<b>Данные активного на данный момент розыгрыша</b>:\n"
            f"Дата создания розыгрыша: <i>{data["date"]}</i>\n"
            f"Количество номерков: <i>{data["numbers_amount"]}</i>\n"
            f"Уже купленные номерки: <i>{" | ".join(data["purchased"].split(","))}</i>\n"
            f"Забронированные номерки: <i>{" | ".join(data["booked"].split(","))}</i>\n"
            f"Цена одного номерка: <i>{data["price"]}</i> ₽"
        )

        await message.answer(text=text,
                             reply_markup=await RKB.back())

        if data["purchased"]:
            purchased = list(map(int, (data['purchased'].split(","))))  # Купленные. Пример: [1, 2, 3]

            text_p = "<b>Владельцы номерков:</b>\n"

            users = await get_all_users()

            for number in purchased:
                for user in users:
                    if not user['numbers']:
                        continue

                    user_numbers = list(map(int, (user['numbers'].split(","))))

                    if number in user_numbers:
                        text_p += (f"\n\tНомерок \"{number}\": {user['id']} - <code>{user['username']}</code> - "
                                   f"{user['fullname']} - <code>{user['phone']}</code>")

            await message.answer(text=text)

        await message.answer_photo(photo=photo,
                                   caption=text_lottery,
                                   parse_mode=ParseMode.MARKDOWN_V2)

    else:
        text += "<b>На данный момент активных розыгрышей нет ⚪️</b>"

        await message.answer(text=text,
                             reply_markup=await RKB.back())


@router.message(F.text == "📝 Изменить сообщения бота", IsAdmin())
@router.message(Command("edit_text"), IsAdmin())
async def command_edit_text_handling(message: Message, state: FSMContext) -> None:
    await message.delete()

    await state.set_state(FSMAdmin.edit_text_1)

    text = "📝 Вы можете изменить следующие сообщения:"

    await message.answer(text=text, reply_markup=await RKB.edit_text())
