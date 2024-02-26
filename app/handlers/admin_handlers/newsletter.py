from aiogram import F, Router, exceptions
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from app.database.bot_functions import check_user_notification, get_users_ids_and_notifications
from app.dispatcher import bot
from app.filters import IsAdmin
from app.fsm import FSMAdmin
from app.keyboards.admin_kb import RKB
from app.texts.functions import newsletter

router = Router()


@router.message(Command("nlet_all"), IsAdmin())
@router.message(F.text.in_(["✉️ Массовая рассылка"]), IsAdmin())
async def command_nlet_all_handling(message: Message, state: FSMContext) -> None:
    """Handle command - /nlet_all, Handle text - ✉️ Массовая рассылка."""
    await message.delete()

    await state.set_state(FSMAdmin.nlet_all_1)

    text = ('Сперва, отправьте картинку сообщения. '
            'Этот пункт можно пропустить, нажав снизу на кнопку "<code>Пропустить ⏭</code>".')
    await message.answer(text=text, reply_markup=await RKB.skip())


@router.message(FSMAdmin.nlet_all_1, IsAdmin())
async def nlet_all_1(message: Message, state: FSMContext) -> None:
    if message.photo:
        photo = message.photo[-1].file_id
    elif message.text == "Пропустить ⏭":
        photo = ""
    else:
        await message.answer(text="<b>Не удалось определить картинку. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    await state.set_state(FSMAdmin.nlet_all_2)
    await state.update_data(photo=photo)

    text = "А теперь, отправьте текст сообщения:"
    await message.answer(text=text, reply_markup=await RKB.back())


@router.message(FSMAdmin.nlet_all_2, IsAdmin())
async def nlet_all_2(message: Message, state: FSMContext) -> None:
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
    await state.set_state(FSMAdmin.nlet_all_3)

    text = "А теперь, подтвердите рассылку, или отмените:"

    await message.answer(text=text, reply_markup=await RKB.concan())


@router.message(F.text.in_(["Подтвердить", "Отменить"]), IsAdmin(), FSMAdmin.nlet_all_3)
async def nlet_all_3(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    text_nlet = data.get("text")
    photo = data.get("photo", "")

    await state.set_state(FSMAdmin.passive)

    if message.text == "Подтвердить":
        text = "<i><b>✉️ Рассылка началась . . . ⚪️</b></i>"
        markup = await RKB.main_commands()

        await message.answer(text=text, reply_markup=markup)

        users = await get_users_ids_and_notifications()

        if not users:
            await message.answer(text="<b><i>В базе данных нет пользователей 🔴</i></b>",
                                 reply_markup=await RKB.back())
            return

        flag = await newsletter(chat_ids=users, text=text_nlet, photo=photo)

        if photo:
            await message.answer_photo(photo=photo, caption=text_nlet)
        else:
            await message.answer(text=text)

        if flag:
            text = "<i><b>✉️ Рассылка закончилась успешно 🟢</b></i>"
        else:
            text = "<b><i>✉️ Рассылка закончилась безуспешно 🔴</i></b>"

        await message.answer(text=text, reply_markup=markup)

    else:
        text = "<b><i>✉️ Рассылка была отменена 🔴</i></b>"
        markup = await RKB.main_commands()

        await message.answer(text=text, reply_markup=markup)


@router.message(Command("nlet_one"), IsAdmin())
@router.message(F.text.in_(["🏷 Отправка пользователю"]), IsAdmin())
async def command_nlet_one_handling(message: Message, state: FSMContext) -> None:
    """Handle command - /nlet_one, Handle text - 🏷 Отправка пользователю."""
    await message.delete()

    await state.set_state(FSMAdmin.nlet_one_1)

    text = "Сперва, отправьте ID того пользователя, кому хотите отправить сообщение:"
    await message.answer(text=text, reply_markup=await RKB.back())


@router.message(FSMAdmin.nlet_one_1, IsAdmin())
async def nlet_one_1(message: Message, state: FSMContext) -> None:
    try:
        await bot.get_chat(message.text)

    except exceptions.TelegramBadRequest:
        await message.answer(text="<b>Не удалось определить ID пользователя. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    user_id = message.text

    await state.set_state(FSMAdmin.nlet_one_2)
    await state.update_data(user_id=user_id)

    text = ("А теперь, отправьте картинку сообщения. "
            'Этот пункт можно пропустить, нажав снизу на кнопку "<code>Пропустить ⏭</code>".')

    await message.answer(text=text, reply_markup=await RKB.skip())


@router.message(FSMAdmin.nlet_one_2, IsAdmin())
async def nlet_one_2(message: Message, state: FSMContext) -> None:
    if message.photo:
        photo = message.photo[-1].file_id
    elif message.text == "Пропустить ⏭":
        photo = ""
    else:
        await message.answer(text="<b>Не удалось определить картинку. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    await state.set_state(FSMAdmin.nlet_one_3)
    await state.update_data(photo=photo)

    text = "А теперь, отправьте текст сообщения:"
    await message.answer(text=text, reply_markup=await RKB.back())


@router.message(FSMAdmin.nlet_one_3, IsAdmin())
async def nlet_one_3(message: Message, state: FSMContext) -> None:
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
    await state.set_state(FSMAdmin.nlet_one_4)

    text = "А теперь, подтвердите отправку, или отмените:"

    await message.answer(text=text, reply_markup=await RKB.concan())


@router.message(F.text.in_(["Подтвердить", "Отменить"]), IsAdmin(), FSMAdmin.nlet_one_4)
async def nlet_one_4(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    text_nlet = data.get("text")
    photo = data.get("photo", "")
    user_id = data.get("user_id")

    await state.set_state(FSMAdmin.passive)

    if message.text == "Подтвердить":
        text = "<i><b>🏷 Идет отправка сообщения пользователю . . . ⚪️</b></i>"
        markup = await RKB.main_commands()

        await message.answer(text=text, reply_markup=markup)

        user_notification = await check_user_notification(user_id=user_id)

        if user_notification is None:
            await message.answer(text="<b><i>🏷 Такого пользователя нету в базе данных 🔴</i></b>",
                                 reply_markup=await RKB.back())
            return

        flag = await newsletter(chat_ids=[user_id, user_notification], text=text_nlet, photo=photo)

        if flag:
            text = "<i><b>🏷 Отправка сообщения пользователю закончилась успешно 🟢</b></i>"
        else:
            text = "<b><i>🏷 Отправка сообщения пользователю закончилась безуспешно 🔴</i></b>"

        await message.answer(text=text, reply_markup=markup)

    else:
        text = "<b><i>🏷 Отправка сообщения пользователю была отменена 🔴</i></b>"
        markup = await RKB.main_commands()

        await message.answer(text=text, reply_markup=markup)
