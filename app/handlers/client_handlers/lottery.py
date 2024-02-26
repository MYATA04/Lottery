import asyncio
import contextlib

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from app.database.bot_functions import (
    check_lottery,
    check_user_notification,
    get_data_lottery,
    get_user_numbers,
    update_booked_lottery_numbers,
)
from app.dispatcher import bot
from app.filters import IsClient
from app.fsm import FSMClient
from app.keyboards.client_kb import IKB, RKB
from app.texts.functions import delete_messages, deleter, send_message_to_user
from app.texts.texts import CLIENTS_TEXTS

router = Router()


@router.message(F.text == "👀 Посмотреть розыгрыш", IsClient(), FSMClient.passive)
async def watch_the_draw(message: Message, state: FSMContext) -> None:  # noqa: PLR0915
    """Handle text - 👀 Посмотреть розыгрыш."""
    await deleter(message=message, state=state)
    await state.update_data(start_il=0)

    check = await check_lottery()

    if not check:
        name = "watch_the_draw_client"
        text = CLIENTS_TEXTS[name]

        markup = await RKB.back()

        await send_message_to_user(chat_id=message.chat.id, name=name, text=text, markup=markup, state=state)

    else:
        await state.set_state(FSMClient.lottery_1)
        lottery_data = await get_data_lottery()

        text = lottery_data["text"]
        photo = lottery_data["photo"]
        price = int(lottery_data["price"])
        numbers_amount = int(lottery_data["numbers_amount"])  # Количество номерков в числовом виде. Пример: 52
        purchased = []
        booked = []

        if lottery_data["purchased"]:
            purchased = list(map(int, (lottery_data["purchased"].split(","))))  # Купленные. Пример: [1, 2, 3]
        if lottery_data["booked"]:
            booked = list(map(int, (lottery_data["booked"].split(","))))  # Забронированные. Пример: [1, 2, 3]

        user_numbers = await get_user_numbers(message.from_user.id)
        markup = await IKB.lottery(
            count=numbers_amount,
            user_numbers=user_numbers,
            purchased=purchased,
            booked=booked,
            state=state,
            price=price,
        )

        var = await message.answer_photo(
            photo=photo, caption=text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=markup
        )

        data = await state.get_data()
        message_ids = data.get("message_ids", [])
        message_ids.append(var.message_id)
        await state.update_data(message_ids=message_ids)

        time = 0

        while True:
            await state.update_data(flag=0)

            await asyncio.sleep(1)
            time += 1

            data = await state.get_data()

            if data["flag"] == 3:  # noqa: PLR2004
                time = 0
                continue

            if data["flag"] == 0 and time >= 60:  # noqa: PLR2004
                await state.update_data(flag=2, start_il=0)
                await state.set_state(FSMClient.passive)

                await delete_messages(state=state, chat_id=message.from_user.id)

                name = "start_client"
                text = CLIENTS_TEXTS[name]

                photo_path = "medias/start_admin.png"

                notification = await check_user_notification(message.from_user.id)
                markup = await RKB.main_commands(notification)

                await send_message_to_user(
                    chat_id=message.chat.id, name=name, text=text, photo_path=photo_path, markup=markup, state=state
                )

                break

            if data["flag"] not in [0, 3]:  # noqa: PLR2004
                break


@router.callback_query(IsClient(), FSMClient.lottery_1, lambda query: query.data in ["l<", "l>"])
async def lottery_1_left_right(query: CallbackQuery, state: FSMContext) -> None:
    lottery_data = await get_data_lottery()
    numbers_amount = int(lottery_data["numbers_amount"])  # Количество номерков в числовом виде. Пример: 52
    start = lottery_data.get("start_il", 0)

    price = int(lottery_data["price"])

    purchased = []
    booked = []

    if lottery_data["purchased"]:
        purchased = list(map(int, (lottery_data["purchased"].split(","))))  # Купленные. Пример: [1, 2, 3]
    if lottery_data["booked"]:
        booked = list(map(int, (lottery_data["booked"].split(","))))  # Забронированные. Пример: [1, 2, 3]

    user_numbers = await get_user_numbers(query.from_user.id)

    if query.data == "l<":
        if start == 0 or numbers_amount <= 9:  # noqa: PLR2004
            await bot.answer_callback_query(callback_query_id=query.id)
            return

        await query.message.edit_reply_markup(
            reply_markup=await IKB.lottery(
                count=numbers_amount,
                user_numbers=user_numbers,
                purchased=purchased,
                booked=booked,
                state=state,
                price=price,
                flag=False,
            )
        )

    elif query.data == "l>":
        if start == numbers_amount or numbers_amount - start <= 9:  # noqa: PLR2004
            await bot.answer_callback_query(callback_query_id=query.id)
            return

        await query.message.edit_reply_markup(
            reply_markup=await IKB.lottery(
                count=numbers_amount,
                user_numbers=user_numbers,
                purchased=purchased,
                booked=booked,
                state=state,
                price=price,
                flag=True,
            )
        )

    await state.update_data(flag=3)


@router.callback_query(IsClient(), lambda query: query.data == "passive")
async def passive_query(query: CallbackQuery) -> None:
    await bot.answer_callback_query(callback_query_id=query.id)


@router.callback_query(FSMClient.lottery_1, IsClient(), lambda query: query.data.startswith("closed"))
async def lottery_1_closed(query: CallbackQuery) -> None:
    number = query.data.split(":")[1]

    text = f'Номерок "{number}" недоступен, выберите похожие на эту номерки для покупки: "11 ⚪️"'
    await bot.answer_callback_query(callback_query_id=query.id, text=text, cache_time=5)


@router.callback_query(IsClient(), FSMClient.lottery_2, lambda query: query.data == "l<<")
async def lottery_2_back(query: CallbackQuery, state: FSMContext) -> None:  # noqa: PLR0915
    await state.set_state(FSMClient.lottery_1)

    data = await state.get_data()
    number = int(data.get("number"))

    with contextlib.suppress(ValueError):
        await update_booked_lottery_numbers(number=number, type_append=False)

    lottery_data = await get_data_lottery()

    text = lottery_data["text"]
    photo = lottery_data["photo"]
    price = int(lottery_data["price"])
    numbers_amount = int(lottery_data["numbers_amount"])  # Количество номерков в числовом виде. Пример: 52
    purchased = []
    booked = []

    if lottery_data["purchased"]:
        purchased = list(map(int, (lottery_data["purchased"].split(","))))  # Купленные. Пример: [1, 2, 3]
    if lottery_data["booked"]:
        booked = list(map(int, (lottery_data["booked"].split(","))))  # Забронированные. Пример: [1, 2, 3]

    user_numbers = await get_user_numbers(query.from_user.id)
    markup = await IKB.lottery(
        count=numbers_amount, user_numbers=user_numbers, purchased=purchased, booked=booked, state=state, price=price
    )

    await delete_messages(state=state, chat_id=query.from_user.id)

    var = await query.message.answer_photo(
        photo=photo, caption=text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=markup
    )

    message_ids = data.get("message_ids", [])
    message_ids.append(var.message_id)
    await state.update_data(message_ids=message_ids)

    time = 0

    while True:
        await state.update_data(flag=0)

        await asyncio.sleep(1)
        time += 1

        data = await state.get_data()

        if data["flag"] == 3:  # noqa: PLR2004
            time = 0
            continue

        if data["flag"] == 0 and time >= 60:  # noqa: PLR2004
            await state.update_data(flag=2, start_il=0)
            await state.set_state(FSMClient.passive)

            await delete_messages(state=state, chat_id=query.from_user.id)

            await query.answer(text="1 минута прошла, попробуйте еще раз.",
                               show_alert=True)

            name = "start_client"
            text = CLIENTS_TEXTS[name]

            photo_path = "medias/start_admin.png"
            notification = await check_user_notification(query.from_user.id)
            markup = await RKB.main_commands(notification)

            await send_message_to_user(
                chat_id=query.from_user.id, name=name, text=text, photo_path=photo_path, markup=markup, state=state
            )

            break

        if data["flag"] not in [0, 3]:  # noqa: PLR2004
            break


@router.callback_query(IsClient(), lambda query: query.data == "menu")
async def back_to_main_menu(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FSMClient.passive)
    await state.update_data(flag=2)

    await delete_messages(state=state, chat_id=query.from_user.id)

    name = "start_client"
    text = CLIENTS_TEXTS[name]

    photo_path = "medias/start_admin.png"
    notification = await check_user_notification(query.from_user.id)
    markup = await RKB.main_commands(notification)

    await send_message_to_user(chat_id=query.from_user.id,
                               name=name,
                               text=text,
                               photo_path=photo_path,
                               markup=markup,
                               state=state)


@router.callback_query(IsClient(), lambda query: query.data == "l<<<", FSMClient.lottery_1)
async def lottery_1_back(query: CallbackQuery, state: FSMContext) -> None:  # noqa: PLR0915
    lottery_data = await get_data_lottery()

    data = await state.get_data()
    number = int(data.get("number"))

    with contextlib.suppress(ValueError):
        await update_booked_lottery_numbers(number=number, type_append=False)

    text = lottery_data["text"]
    photo = lottery_data["photo"]
    price = int(lottery_data["price"])
    numbers_amount = int(lottery_data["numbers_amount"])  # Количество номерков в числовом виде. Пример: 52
    purchased = []
    booked = []

    if lottery_data["purchased"]:
        purchased = list(map(int, (lottery_data["purchased"].split(","))))  # Купленные. Пример: [1, 2, 3]
    if lottery_data["booked"]:
        booked = list(map(int, (lottery_data["booked"].split(","))))  # Забронированные. Пример: [1, 2, 3]

    user_numbers = await get_user_numbers(query.from_user.id)
    markup = await IKB.lottery(
        count=numbers_amount,
        user_numbers=user_numbers,
        purchased=purchased,
        booked=booked,
        state=state,
        price=price
    )

    await delete_messages(state=state, chat_id=query.from_user.id)

    var = await query.message.answer_photo(
        photo=photo, caption=text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=markup
    )

    message_ids = data.get("message_ids", [])
    message_ids.append(var.message_id)
    await state.update_data(message_ids=message_ids)

    time = 0

    while True:
        await state.update_data(flag=0)

        await asyncio.sleep(1)
        time += 1

        data = await state.get_data()

        if data["flag"] == 3:  # noqa: PLR2004
            time = 0
            continue

        if data["flag"] == 0 and time >= 60:  # noqa: PLR2004
            await state.update_data(flag=2, start_il=0)
            await state.set_state(FSMClient.passive)

            await delete_messages(state=state, chat_id=query.from_user.id)

            await query.answer(text="1 минута прошла, попробуйте еще раз.",
                               show_alert=True)

            name = "start_client"
            text = CLIENTS_TEXTS[name]

            photo_path = "medias/start_admin.png"
            notification = await check_user_notification(query.from_user.id)
            markup = await RKB.main_commands(notification)

            await send_message_to_user(
                chat_id=query.from_user.id, name=name, text=text, photo_path=photo_path, markup=markup, state=state
            )

            break

        if data["flag"] not in [0, 3]:  # noqa: PLR2004
            break
