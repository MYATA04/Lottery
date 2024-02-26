from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class IKB:
    """Class with inline keyboard functions."""

    @staticmethod
    async def clet_test(  # noqa: C901, PLR0912
            count: int, user_numbers: list[int, Any], state: FSMContext, price: int, flag: bool = None
    ) -> InlineKeyboardMarkup:
        data = await state.get_data()
        start = data.get("start_il", 0)

        keyboard = [
            [
                InlineKeyboardButton(text="-".join(map(str, user_numbers)), callback_data="passive")
            ]
        ]

        if flag is not None:
            if not flag:
                if start % 9 == 0 and start >= 18:  # noqa: PLR2004
                    start -= 9

                elif start < 18:  # noqa: PLR2004
                    start = 0

                else:
                    start = start % 9

            elif flag:
                if start + 9 > count:
                    start = count
                else:
                    start += 9

        keys = []
        for i in range(start, start + 9):
            number = i + 1

            if number - 1 >= count:
                break

            keys.append(InlineKeyboardButton(text=f"{number} ⚪️", callback_data=f"test:{number}"))

            if len(keys) == 3:  # noqa: PLR2004
                keyboard.append(keys)
                keys = []

        if keys:
            keyboard.append(keys)

        keyboard.append(
            [
                InlineKeyboardButton(text="«", callback_data="test<"),
                InlineKeyboardButton(text=str(count), callback_data="passive"),
                InlineKeyboardButton(text="»", callback_data="test>")
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(text=f"Цена: {price} ₽", callback_data="passive")
            ]
        )

        if flag is None:
            if start + 9 > count:
                start = count
            else:
                start += 9

        await state.update_data(start_il=start)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    async def clet_test_p(  # noqa: C901, PLR0912
            price: int, state: FSMContext, count: int, number: int
    ) -> InlineKeyboardMarkup:
        data = await state.get_data()
        start = data.get("start_il", 0)

        keyboard = [
            [
                InlineKeyboardButton(text=f"Оплатить {price} ₽", callback_data="passive")
            ],
            [
                InlineKeyboardButton(text=f"Выбранный номерок: {number}", callback_data="passive")
            ],
            [
                InlineKeyboardButton(text="«", callback_data="test<<")
            ]
        ]

        if start + 9 > count:
            start = count
        else:
            start += 9

        await state.update_data(start_il=start)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    async def request_adress_reply(user_id: int | str) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(text="Ответить победителю 🔥", callback_data=f"request_adress_reply:{user_id}")]
        ]

        return InlineKeyboardMarkup(inline_keyboard=keyboard)
