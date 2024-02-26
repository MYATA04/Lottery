from aiogram import F, Router, exceptions
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from app.filters import IsAdmin
from app.fsm import FSMAdmin
from app.keyboards.admin_kb import RKB
from app.texts.functions import get_message, send_message_to_user, set_message
from app.texts.texts import CLIENTS_TEXTS

router = Router()


@router.message(FSMAdmin.edit_text_1, IsAdmin())
async def edit_text_1(message: Message, state: FSMContext) -> None:
    await message.delete()

    photo_path = None

    if message.text == "Стартовое сообщение":
        text = ('<i>Это сообщение выводится, когда пользователь запускает бота и когда пользователь отправляет '
                'текстовую команду: "🔖 Перейти в главное меню"')
        await message.answer(text=text)

        name = "start_client"

        photo_path = "medias/start_admin.png"

    elif message.text == "Сообщение правил":
        text = '<i>Это сообщение выводится, когда пользователь отправляет текстовую команду: "📑 Правила розыгрыша"</i>'
        await message.answer(text=text)

        name = "rules_client"

    elif message.text == "Сообщение контактов":
        text = '<i>Это сообщение выводится, когда пользователь отправляет текстовую команду: "📞 Контакты"</i>'
        await message.answer(text=text)

        name = "admins_contacts_client"

    elif message.text == "Сообщение победителей":
        text = ("<i>Это сообщение выводится победившим в розыгрыше участникам, после того как будут куплены все "
                "номерки</i>")
        await message.answer(text=text)

        name = "winners_client"

    elif message.text == "Сообщение проигравших":
        text = ("<i>Это сообщение выводится проигравшим в розыгрыше участникам, после того как будут куплены все "
                "номерки</i>")
        await message.answer(text=text)

        name = "losed_client"

    elif message.text == "Сообщение объявления розыгрыша":
        text = ("<i>Это сообщение отправляется всем пользователям, у которых включено уведомление, после того как "
                "будет создан новый розыгрыш</i>")
        await message.answer(text=text)

        name = "lottery_created_client"

    elif message.text == "Сообщение спроса адреса доставки":
        text = ("<i>Это сообщение отправляется победителю розыгрыша, после того как он начнет действие с отправкой "
                "адреса доставки</i>")
        await message.answer(text=text)

        name = "request_adress"

    elif message.text == "Сообщение принятия адреса доставки":
        text = "<i>Это сообщение отправляется победителю розыгрыша, после того как он отправит адреса доставки</i>"
        await message.answer(text=text)

        name = "response_adress"

    else:
        return

    await state.set_state(FSMAdmin.edit_text_2)

    text = CLIENTS_TEXTS[name]

    await send_message_to_user(chat_id=message.chat.id,
                               name=name,
                               text=text,
                               photo_path=photo_path)

    await state.update_data(name=name)

    text = (f"Вы выбрали: {message.text}\n"
            f"Сверху вы можете увидеть его сообщение 👆\n\n"
            f'Сперва, отправьте картинку сообщения. Этот пункт можно пропустить, нажав снизу на кнопку '
            f'"<code>Пропустить ⏭</code>, что бы оставить картинку как есть, '
            f'или нажмите на кнопку "<code>🗑 Убрать картинку</code>", что бы сообщение было без картинки. '
            'Для перехода в главное меню, нажите на кнопку снизу "<code>🔖 Перейти в главное меню</code>"')

    await message.answer(text=text, reply_markup=await RKB.skip_or_delete_photo())


@router.message(FSMAdmin.edit_text_2, IsAdmin())
async def edit_text_2(message: Message, state: FSMContext) -> None:
    if message.photo:
        photo = message.photo[-1].file_id

    elif message.text == "Пропустить ⏭":
        data = await state.get_data()
        data_message = await get_message(data["name"])
        photo = data_message.get("photo", "")

    elif message.text == "🗑 Убрать картинку":
        photo = ""

    else:
        await message.answer(text="<b>Не удалось определить картинку. Пожалуйста, попробуйте еще раз 🟡</b>",
                             reply_markup=await RKB.back())
        return

    await state.update_data(photo=photo)
    await state.set_state(FSMAdmin.edit_text_3)

    text = "А теперь, отправьте текст сообщения:"

    await message.answer(text=text, reply_markup=await RKB.back())


@router.message(FSMAdmin.edit_text_3, IsAdmin())
async def edit_text_3(message: Message, state: FSMContext) -> None:
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
    await state.set_state(FSMAdmin.edit_text_4)

    text = "А теперь, подтвердите изменение, или отмените:"

    await message.answer(text=text, reply_markup=await RKB.concan())


@router.message(F.text.in_(["Подтвердить", "Отменить"]), IsAdmin(), FSMAdmin.edit_text_4)
async def edit_text_4(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    name = data.get("name")
    text = data.get("text")
    photo = data.get("photo", "")

    if message.text == "Подтвердить":
        await set_message(name=name, text=text, photo=photo)

        text = "<i><b>📝 Изменение сообщения успешно сохранено 🟢</b></i>"
        markup = await RKB.main_commands()

        await message.answer(text=text, reply_markup=markup)

    else:
        text = "<b><i>📝 Изменение сообщения успешно отменено 🔴</i></b>"
        markup = await RKB.main_commands()

        await message.answer(text=text, reply_markup=markup)

    await state.set_state(FSMAdmin.passive)
