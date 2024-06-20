from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_start_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Get Monthly Statistics",
            callback_data="get_monthly"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Create an Expense",
            callback_data="create_expense"
        ),
        types.InlineKeyboardButton(
            text="Create a Category",
            callback_data="create_category"
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Delete an Expense",
            callback_data="delete_expense"
        ),
        types.InlineKeyboardButton(
            text="Delete a Category",
            callback_data="delete_category"
        ),
    )

    return builder.as_markup()


def get_daily_kb():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Get Daily Statistics",
            callback_data="get_daily"
        )
    )

    return builder.as_markup()
