import contextlib

from aiogram import Router, exceptions
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config_reader import config
from app.database.bot_functions import check_user_notification, get_user
from app.dispatcher import bot
from app.filters import IsClient
from app.fsm import FSMClient
from app.keyboards.client_kb import RKB
from app.texts.functions import delete_messages, deleter, send_message_to_user
from app.texts.texts import CLIENTS_TEXTS

router = Router()


@router.callback_query(IsClient(), lambda query: query.data.startswith("request_address"), FSMClient.passive)
async def request_address(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FSMClient.request_address_1)
    await delete_messages(state, query.from_user.id)

    await state.update_data(adress_msg_id=query.message.message_id)

    number = int(query.data.split(":")[1])
    await state.update_data(number=number)

    name = "request_adress"
    text = CLIENTS_TEXTS[name]

    await query.message.edit_reply_markup(reply_markup=None)
    await send_message_to_user(chat_id=query.from_user.id,
                               name=name,
                               text=text,
                               state=state)


@router.message(IsClient(), FSMClient.request_address_1)
async def request_address_1(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer(text="<b>Не удалось определить текст сообщения. Пожалуйста, попробуйте еще раз 🟡</b>")
        return

    await state.set_state(FSMClient.request_address_2)
    await state.update_data(adress=message.text)

    text = "А теперь, подтвердите отправку адреса для доставки, или отмените:"
    var = await message.answer(text=text, reply_markup=await RKB.concan())

    data = await state.get_data()
    message_ids = data.get("message_ids", [])
    message_ids.append(message.message_id)
    message_ids.append(var.message_id)
    await state.update_data(message_ids=message_ids)


@router.message(IsClient(), FSMClient.request_address_2, lambda message: message.text in ["Подтвердить", "Отменить"])
async def request_address_2(message: Message, state: FSMContext) -> None:
    await deleter(message, state)
    await state.set_state(FSMClient.passive)

    if message.text == "Отменить":
        name = "start_client"
        text = CLIENTS_TEXTS[name]

        photo_path = "medias/start_admin.png"
        notification = await check_user_notification(message.from_user.id)
        markup = await RKB.main_commands(notification)

        await send_message_to_user(chat_id=message.chat.id,
                                   name=name,
                                   text=text,
                                   photo_path=photo_path,
                                   markup=markup,
                                   state=state)

    else:
        data = await state.get_data()
        adress_msg_id = data['adress_msg_id']
        await bot.delete_messages(chat_id=message.chat.id,
                                  message_ids=adress_msg_id)

        number = data['number']
        adress = data['adress']
        user = await bot.get_chat(chat_id=message.from_user.id)
        user_db = await get_user(user_id=user.id)

        text_to_admins = ("<b>🎉 Победитель отправил адрес для доставки приза:</b>\n\n"
                          f"Номерок: <u>{number}</u>\n"
                          f"Телеграм ID: <code><i>{user.id}</i></code>\n"
                          f"Имя пользователя (@username): <code><i>{user.username}</i></code>\n"
                          f"Полное имя: <code><i>{user.full_name}</i></code>\n"
                          f"Номер телефона: <code><i>{user_db['phone']}</i></code>\n\n"
                          f"Адрес для доставки: <code><i>{adress}</i></code>\n\n"
                          f"Отправить сообщение пользователю можно командой - /nlet_one или текстовой командой "
                          f"\"<code>🏷 Отправка пользователю</code>\"")

        for admin_id in config.ADMINS_IDS:
            with contextlib.suppress(exceptions.TelegramForbiddenError, exceptions.TelegramBadRequest):
                await bot.send_message(chat_id=admin_id, text=text_to_admins)

        name = "response_adress"
        text = CLIENTS_TEXTS[name]
        markup = await RKB.back()

        await send_message_to_user(chat_id=message.from_user.id,
                                   name=name,
                                   text=text,
                                   markup=markup,
                                   state=state)
