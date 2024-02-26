from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class RKB:
    """Class with reply keyboard functions."""

    @staticmethod
    async def main_commands(notification: bool = False) -> ReplyKeyboardMarkup:
        keyboards = [
            [KeyboardButton(text="📑 Правила розыгрыша")],
            [KeyboardButton(text="📝 Посмотреть текущий розыгрыш")],
            [KeyboardButton(text="📞 Контакты")],
        ]

        if notification:
            keyboards.append([KeyboardButton(text="🔕 Отключить уведомления")])

        else:
            keyboards.append([KeyboardButton(text="🔔 Включить уведомления")])

        return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboards)

    @staticmethod
    async def back() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[[KeyboardButton(text="🔖 Перейти в главное меню")]],
        )

    @staticmethod
    async def back_or_lottery() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text="👀 Посмотреть розыгрыш")],
                [KeyboardButton(text="🔖 Перейти в главное меню")],
            ],
        )

    @staticmethod
    async def concan() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text="Подтвердить")],
                [KeyboardButton(text="Отменить")]
            ],
        )
