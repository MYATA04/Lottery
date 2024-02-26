from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class RKB:
    """Class with reply keyboard functions."""

    @staticmethod
    async def main_commands() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text="🎉 Создать розыгрыш")],
                [KeyboardButton(text="📝 Изменить сообщения бота")],
                [KeyboardButton(text="✉️ Массовая рассылка")],
                [KeyboardButton(text="🏷 Отправка пользователю")],
                [KeyboardButton(text="🗃 Статистика")],
                [KeyboardButton(text="🆘 Помощь по командам")],
            ],
        )

    @staticmethod
    async def edit_text() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text="Стартовое сообщение")],
                [KeyboardButton(text="Сообщение правил")],
                [KeyboardButton(text="Сообщение победителей")],
                [KeyboardButton(text="Сообщение проигравших")],
                [KeyboardButton(text="Сообщение контактов")],
                [KeyboardButton(text="Сообщение объявления розыгрыша")],
                [KeyboardButton(text="Сообщение спроса адреса доставки")],
                [KeyboardButton(text="Сообщение принятия адреса доставки")],
                [KeyboardButton(text="🔖 Перейти в главное меню")],
            ],
        )

    @staticmethod
    async def back() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[[KeyboardButton(text="🔖 Перейти в главное меню")]],
        )

    @staticmethod
    async def skip_or_delete_photo() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text="Пропустить ⏭")],
                [KeyboardButton(text="🗑 Убрать картинку")],
                [KeyboardButton(text="🔖 Перейти в главное меню")],
            ],
        )

    @staticmethod
    async def skip() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[[KeyboardButton(text="Пропустить ⏭")], [KeyboardButton(text="🔖 Перейти в главное меню")]],
        )

    @staticmethod
    async def concan() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[[KeyboardButton(text="Подтвердить")], [KeyboardButton(text="Отменить")]],
        )
