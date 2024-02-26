from datetime import datetime

import pytz
from aiogram import F, Router, exceptions
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from app.database.bot_functions import check_lottery, get_users_ids_and_notifications, set_data_lottery
from app.dispatcher import bot
from app.filters import IsAdmin
from app.fsm import FSMAdmin
from app.keyboards.admin_kb import IKB, RKB
from app.scheduler.functions import start_interval_lottery
from app.texts.functions import send_message_to_user
from app.texts.texts import CLIENTS_TEXTS

router = Router()


@router.message(Command("clet"), IsAdmin())
@router.message(F.text.in_(["🎉 Создать розыгрыш"]), IsAdmin())
async def command_clet_handling(message: Message, state: FSMContext) -> None:
    await message.delete()
    await state.update_data(start_il=0)

    if await check_lottery():
        text = "<b><i>На данный момент уже есть активный розыгрыш ⚪️</i></b>"
        await message.answer(text=text, reply_markup=await RKB.back())
        return

    await state.set_state(FSMAdmin.clet_1)

    text = "Сперва, отправьте картинку сообщения розыгрыша:"
    await message.answer(text=text, reply_markup=await RKB.back())


@router.message(FSMAdmin.clet_1, IsAdmin())
async def clet_1(message: Message, state: FSMContext) -> None:
    if message.photo:
        photo = message.photo[-1].file_id

    else:
        await message.answer(text="<b>Не удалось определить картинку. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    await state.set_state(FSMAdmin.clet_2)
    await state.update_data(photo=photo)

    text = "А теперь, отправьте текст или описание сообщения розыгрыша:"
    await message.answer(text=text, reply_markup=await RKB.back())


@router.message(FSMAdmin.clet_2, IsAdmin())
async def clet_2(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer(text="<b>Не удалось определить текст сообщения. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    text = message.md_text

    data = await state.get_data()
    photo = data.get("photo", "")

    try:
        if photo:
            await message.answer_photo(photo=photo, caption=text, parse_mode=ParseMode.MARKDOWN_V2)

        else:
            await message.answer(text=text, parse_mode=ParseMode.MARKDOWN_V2)

    except exceptions.TelegramBadRequest:
        await message.answer(text="<b>Текст под картинкой слишком длинный. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    await state.update_data(text=text)
    await state.set_state(FSMAdmin.clet_3)

    text = "А теперь, отправьте количество номерков (натуральное число, больше 0):"
    await message.answer(text=text, reply_markup=await RKB.back())


@router.message(FSMAdmin.clet_3, IsAdmin())
async def clet_3(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer(text="<b>Не удалось определить текст сообщения. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    elif not message.text.isdigit() or int(message.text) <= 0:  # noqa: RET505
        await message.answer(text="<b>Не удалось определить числовое значение. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    await state.set_state(FSMAdmin.clet_4)
    await state.update_data(count=int(message.text))

    text = "А теперь, отправьте количество победных номерков (натуральное число, больше 0):"
    await message.answer(text=text, reply_markup=await RKB.back())


@router.message(FSMAdmin.clet_4, IsAdmin())
async def clet_4(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer(text="<b>Не удалось определить текст сообщения. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    elif not message.text.isdigit() or int(message.text) <= 0:  # noqa: RET505
        await message.answer(text="<b>Не удалось определить числовое значение. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    await state.set_state(FSMAdmin.clet_5)
    await state.update_data(win_numbers_amount=int(message.text))

    text = "А теперь, отправьте цену одного номерка (рубли, натуральное число, больше 0):"
    await message.answer(text=text, reply_markup=await RKB.back())


@router.message(FSMAdmin.clet_5, IsAdmin())
async def clet_5(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer(text="<b>Не удалось определить текст сообщения. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return
    elif not message.text.isdigit() or int(message.text) <= 0:  # noqa: RET505
        await message.answer(text="<b>Не удалось определить числовое значение. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    await state.set_state(FSMAdmin.clet_6)
    await state.update_data(price=int(message.text))

    data = await state.get_data()
    photo = data.get("photo")
    text = data.get("text")
    count = int(data.get("count"))
    user_numbers = ["У вас пока нет номерков"]
    win_numbers_amount = data.get("win_numbers_amount")
    price = int(data.get("price"))

    await message.answer_photo(photo=photo,
                               caption=text,
                               parse_mode=ParseMode.MARKDOWN_V2,
                               reply_markup=await IKB.clet_test(count=count,
                                                                user_numbers=user_numbers,
                                                                state=state,
                                                                price=price))

    text = (f"А теперь, подтвердите создание розыгрыша, или отмените. Вот данные:\n\n"
            f"Общее количество номерков: <i>{count}</i>\n"
            f"Количество победных номерков: <i>{win_numbers_amount}</i>\n"
            f"Цена одного номерка: <i>{price}</i>")
    await message.answer(text=text, reply_markup=await RKB.concan())


@router.callback_query(lambda query: query.data in ["test<", "test>", "test<<"] or query.data.startswith("test:"),
                       IsAdmin(), FSMAdmin.clet_6)
async def query_clet_6(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    start = data.get("start_il", 0)
    count = int(data.get("count"))
    user_numbers = ["У вас пока нет номерков"]
    price = int(data.get("price"))

    if query.data.startswith("test:"):
        number = int(query.data.split(":")[1])

        await query.message.edit_reply_markup(
            reply_markup=await IKB.clet_test_p(
                count=count,
                number=number,
                state=state,
                price=price)
        )

    elif query.data == "test<":
        if start == 0 or count <= 9:  # noqa: PLR2004
            await bot.answer_callback_query(callback_query_id=query.id)
            return

        await query.message.edit_reply_markup(
            reply_markup=await IKB.clet_test(
                count=count,
                user_numbers=user_numbers,
                state=state,
                flag=False,
                price=price)
        )

    elif query.data == "test<<":
        await query.message.edit_reply_markup(
            reply_markup=await IKB.clet_test(
                count=count,
                user_numbers=user_numbers,
                state=state,
                flag=False,
                price=price)
        )

    elif query.data == "test>":
        if start == count or count - start <= 9:  # noqa: PLR2004
            await bot.answer_callback_query(callback_query_id=query.id)
            return

        await query.message.edit_reply_markup(
            reply_markup=await IKB.clet_test(
                count=count, user_numbers=user_numbers, state=state, flag=True, price=price)
        )


@router.callback_query(IsAdmin(), lambda query: query.data == "passive")
async def other_clet_6(query: CallbackQuery) -> None:
    await bot.answer_callback_query(callback_query_id=query.id)


@router.message(F.text.in_(["Подтвердить", "Отменить"]), IsAdmin(), FSMAdmin.clet_6)
async def clet_6(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    text = data.get("text")
    photo = data.get("photo")
    count = int(data.get("count"))
    price = int(data.get("price"))
    win_numbers_amount = data.get("win_numbers_amount")

    await state.set_state(FSMAdmin.passive)

    if message.text == "Подтвердить":
        moscow_tz = pytz.timezone("Europe/Moscow")
        date = datetime.now(tz=moscow_tz).strftime("%Y-%m-%d %H:%M:%S")

        await set_data_lottery(text=text,
                               photo_id=photo,
                               numbers_amount=count,
                               price=price,
                               win_numbers_amount=win_numbers_amount,
                               date=date)

        text = "<i><b>🎉 Розыгрыш успешно создан 🟢</b></i>"
        markup = await RKB.main_commands()

        await message.answer(text=text, reply_markup=markup)

        await start_interval_lottery()

        name = "lottery_created_client"
        text = CLIENTS_TEXTS[name]

        users = await get_users_ids_and_notifications()

        if not users:
            return

        for user in users:
            user_id = user[0]
            notification = user[1]

            if notification:
                await send_message_to_user(chat_id=user_id,
                                           name=name,
                                           text=text,
                                           state=state)

    else:
        text = "<b><i>🎉 Создание розыгрыша успешно отменено 🔴</i></b>"
        markup = await RKB.main_commands()

        await message.answer(text=text, reply_markup=markup)
