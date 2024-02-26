from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class IKB:
    """Class with inline keyboard functions."""

    @staticmethod
    async def request_address(number: str | int) -> InlineKeyboardMarkup:
        """Инлайновая клавиатура для получения адреса доставки выигрышного приза для победителей."""
        keyboard = [
            [InlineKeyboardButton(text="📬", callback_data=f"request_address:{number}")],
        ]

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    async def lottery(  # noqa: C901, PLR0912
            count: int,
            user_numbers: list[int, Any],
            purchased: list[int, Any],
            booked: list[int, Any],
            state: FSMContext,
            price: int,
            flag: bool = None
    ) -> InlineKeyboardMarkup:
        """Инлайновая клавиатура, которая используется при покупке номерка в розыгрыше."""
        data = await state.get_data()
        start = data.get("start_il", 0)

        keyboard = [
            [
                InlineKeyboardButton(text="-".join(map(str, user_numbers)), callback_data="passive")
            ]
        ]

        if not user_numbers:
            keyboard[0] = [
                InlineKeyboardButton(text="У вас пока нет номерков", callback_data="passive")
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

            if number in user_numbers:
                qtext = f"{number} 🟢"
                qdata = f"closed:{number}"

            elif number in purchased:
                qtext = f"{number} 🔴"
                qdata = f"closed:{number}"

            elif number in booked:
                qtext = f"{number} 🟡"
                qdata = f"closed:{number}"

            else:
                qtext = f"{number} ⚪️️"
                qdata = f"opened:{number}"

            keys.append(InlineKeyboardButton(text=qtext, callback_data=qdata))

            if len(keys) == 3:  # noqa: PLR2004
                keyboard.append(keys)
                keys = []

        if keys:
            keyboard.append(keys)

        keyboard.append(
            [
                InlineKeyboardButton(text="«", callback_data="l<"),
                InlineKeyboardButton(text=str(count), callback_data="passive"),
                InlineKeyboardButton(text="»", callback_data="l>")
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(text=f"Цена: {price} ₽", callback_data="passive")
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(text="🔖 Перейти в главное меню", callback_data="menu")
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
    async def lottery_buy_number(  # noqa: C901, PLR0912
            state: FSMContext, count: int, price: int
    ) -> InlineKeyboardMarkup:
        """Инлайновая клавиатура, которая используется при покупке номерка."""
        data = await state.get_data()
        start = data.get("start_il", 0)

        keyboard = [
            [
                InlineKeyboardButton(text=f"Оплатить: {price} ₽", pay=True)
            ],
            [
                InlineKeyboardButton(text="«", callback_data="l<<")
            ]
        ]

        if start + 9 > count:
            start = count
        else:
            start += 9

        await state.update_data(start_il=start)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    async def back_lottery() -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text="🔖 Перейти в главное меню", callback_data="menu")
            ],
            [
                InlineKeyboardButton(text="«", callback_data="l<<<")
            ]
        ]

        return InlineKeyboardMarkup(inline_keyboard=keyboard)
