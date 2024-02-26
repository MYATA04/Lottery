import asyncio

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from app.config_reader import config
from app.database.bot_functions import (
    check_user_notification,
    get_data_lottery,
    get_user_numbers,
    update_booked_lottery_numbers,
    update_purchased_lottery_numbers,
    update_purchased_user_numbers,
    update_user_data,
)
from app.dispatcher import bot
from app.filters import IsClient
from app.fsm import FSMClient
from app.keyboards.client_kb import IKB, RKB
from app.texts.functions import delete_messages, send_message_to_user
from app.texts.texts import CLIENTS_TEXTS

router = Router()


@router.callback_query(FSMClient.lottery_1, IsClient(), lambda query: query.data.startswith("opened"))
async def order(query: CallbackQuery, state: FSMContext) -> None:  # noqa: PLR0915
    number = int(query.data.split(":")[1])

    lottery_data = await get_data_lottery()
    numbers_amount = int(lottery_data["numbers_amount"])  # Количество номерков в числовом виде. Пример: 52
    purchased = []
    booked = []

    if lottery_data["purchased"]:
        purchased = list(map(int, (lottery_data["purchased"].split(","))))  # Купленные. Пример: [1, 2, 3]
    if lottery_data["booked"]:
        booked = list(map(int, (lottery_data["booked"].split(","))))  # Забронированные. Пример: [1, 2, 3]

    user_numbers = await get_user_numbers(query.from_user.id)
    zipper = purchased + booked + user_numbers
    price = int(lottery_data["price"])

    if number in zipper:
        text = f'Номерок "{number}" уже недоступен'
        await bot.answer_callback_query(callback_query_id=query.id, text=text, cache_time=5)
        return

    await update_booked_lottery_numbers(number=number)
    await state.set_state(FSMClient.lottery_2)
    await state.update_data(number=number)

    await query.message.edit_reply_markup(reply_markup=None)
    var = await bot.send_invoice(
        chat_id=query.from_user.id,
        title=f'Номерок "{number}"',
        description="Данный номерок будет занят на 15 минут для других пользователей, и вы должны успеть купить "
                    "данный номерок за это время 🟡",
        payload="Pay number",
        provider_token=config.PAY_TOKEN,
        currency="rub",
        prices=[
            LabeledPrice(
                label=f'Номерок "{number}"',
                amount=price * 100
            )
        ],
        start_parameter="lottery_bot",
        need_name=True,
        need_phone_number=True,
        protect_content=True,
        reply_markup=await IKB.lottery_buy_number(count=numbers_amount, state=state, price=price)
    )

    data = await state.get_data()
    message_ids = data.get("message_ids", [])
    message_ids.append(var.message_id)
    await state.update_data(message_ids=message_ids)

    start = data.get("start_il")

    if start % 9 == 0 and start >= 18:  # noqa: PLR2004
        start -= 9

    elif start < 18:  # noqa: PLR2004
        start = 0

    else:
        start = start % 9

    await state.update_data(start_il=start)

    time = 0

    while True:
        await state.update_data(flag=1)

        await asyncio.sleep(1)
        time += 1

        data = await state.get_data()

        if data["flag"] == 1 and time >= 900:  # noqa: PLR2004
            await state.update_data(flag=2)
            await state.set_state(FSMClient.passive)

            await delete_messages(state=state, chat_id=query.from_user.id)

            await update_booked_lottery_numbers(number=number, type_append=False)

            await query.answer(text="15 минут прошли, попробуйте еще раз.",
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

        if data["flag"] != 1:  # noqa: PLR2004
            break


@router.pre_checkout_query(FSMClient.lottery_2, IsClient())
async def pre_checkout_query(query: PreCheckoutQuery) -> None:
    await bot.answer_pre_checkout_query(query.id, ok=True)


@router.message(FSMClient.lottery_2, IsClient())
async def successful_payment(message: Message, state: FSMContext) -> None:
    await state.update_data(flag=2)
    await asyncio.sleep(1.5)
    await delete_messages(state=state, chat_id=message.chat.id)
    await state.set_state(FSMClient.lottery_1)

    pmnt = message.successful_payment.order_info
    phone_number = pmnt.phone_number

    data = await state.get_data()
    number = int(data["number"])

    await update_booked_lottery_numbers(number=number, type_append=False)

    text = f'🎉 Поздравляем! Вы купили номерок "{number}" 🟢!'
    var = await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=await IKB.back_lottery())

    message_ids = data.get("message_ids", [])
    message_ids.append(var.message_id)
    await state.update_data(message_ids=message_ids)

    await update_user_data(user_id=message.from_user.id, column="phone", new_data=str(phone_number))
    await update_purchased_user_numbers(user_id=message.from_user.id, number=number)
    await update_purchased_lottery_numbers(number=number)
