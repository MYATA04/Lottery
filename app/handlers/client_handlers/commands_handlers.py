import contextlib

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from app.database.bot_functions import check_user_notification, set_user_notification, update_booked_lottery_numbers
from app.filters import IsClient
from app.fsm import FSMClient
from app.keyboards.client_kb import RKB
from app.texts.functions import deleter, send_message_to_user
from app.texts.texts import CLIENTS_TEXTS

router = Router()


@router.message(CommandStart(), IsClient())
@router.message(F.text.in_(["🔖 Перейти в главное меню"]), IsClient())
async def command_start_handling(message: Message, state: FSMContext) -> None:
    await deleter(message=message, state=state)
    await state.set_state(FSMClient.passive)

    data = await state.get_data()
    with contextlib.suppress(TypeError):
        number = int(data.get("number"))

        with contextlib.suppress(ValueError):
            await update_booked_lottery_numbers(number=number, type_append=False)

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


@router.message(F.text == "📑 Правила розыгрыша", IsClient(), FSMClient.passive)
async def rules_lottery(message: Message, state: FSMContext) -> None:
    await deleter(message=message, state=state)

    name = "rules_client"
    text = CLIENTS_TEXTS[name]

    markup = await RKB.back()

    await send_message_to_user(chat_id=message.chat.id,
                               name=name,
                               text=text,
                               markup=markup,
                               state=state)


@router.message(F.text == "📝 Посмотреть текущий розыгрыш", IsClient(), FSMClient.passive)
async def active_lottery(message: Message, state: FSMContext) -> None:
    await deleter(message=message, state=state)

    text = ('Если вы еще не прочитали "<code>📑 Правила розыгрыша</code>", настоятельно рекомендуем его прочитать, '
            "это очень важно 🟡 🟡 🟡 В и ном случае, у вас могут быть проблемы с пониманием розыгрыша. Вы можете "
            'перейти на главное меню отправив текстовую команду "<code>🔖 Перейти в главное меню</code>"')
    markup = await RKB.back_or_lottery()

    await send_message_to_user(chat_id=message.chat.id,
                               text=text,
                               markup=markup,
                               state=state)


@router.message(F.text == "📞 Контакты", IsClient(), FSMClient.passive)
async def admins_contacts(message: Message, state: FSMContext) -> None:
    await deleter(message=message, state=state)

    name = "admins_contacts_client"
    text = CLIENTS_TEXTS[name]

    markup = await RKB.back()

    await send_message_to_user(chat_id=message.chat.id,
                               name=name,
                               text=text,
                               markup=markup,
                               state=state)


@router.message(F.text.in_(["🔔 Включить уведомления", "🔕 Отключить уведомления"]), IsClient(), FSMClient.passive)
async def notifications_handle(message: Message, state: FSMContext) -> None:
    await deleter(message=message, state=state)

    if message.text == "🔔 Включить уведомления":
        text = ("🔔 Теперь вам будут приходить уведомления, новости и рассылочные сообщения, а так же уведомление о том, "
                "что создался новый розыгрыш 🟢")

        await set_user_notification(message.from_user.id, notification=True)

    else:
        text = ("🔕 Теперь вам не будут приходить уведомления, новости и рассылочные сообщения, а так же уведомление о "
                "том, что создался новый розыгрыш 🔴")

        await set_user_notification(message.from_user.id, notification=False)

    markup = await RKB.back()

    await send_message_to_user(chat_id=message.chat.id,
                               text=text,
                               markup=markup,
                               state=state)
