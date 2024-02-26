from aiogram.fsm.state import State, StatesGroup


class FSMAdmin(StatesGroup):
    """Машинное состояние для администраторов бота"""
    passive = State()

    edit_text_1 = State()
    edit_text_2 = State()
    edit_text_3 = State()
    edit_text_4 = State()

    nlet_all_1 = State()
    nlet_all_2 = State()
    nlet_all_3 = State()

    nlet_one_1 = State()
    nlet_one_2 = State()
    nlet_one_3 = State()
    nlet_one_4 = State()

    clet_1 = State()
    clet_2 = State()
    clet_3 = State()
    clet_4 = State()
    clet_5 = State()
    clet_6 = State()


class FSMClient(StatesGroup):
    """Машинное состояние для пользователей бота"""
    passive = State()

    lottery_1 = State()
    lottery_2 = State()
    lottery_3 = State()

    request_address_1 = State()
    request_address_2 = State()
