from datetime import datetime

import pytz
from aiogram import types, filters, md
from aiogram.utils.formatting import Text, as_marked_list, as_section, as_marked_section, as_list, Bold, Code
from tortoise import timezone

from . import router
from wrap.apps.expenses import ExpenseCRUD, Expense
from ...apps.categories import Category
from ...apps.users import UserCRUD


async def map_cat_to_expense(expenses: list[Expense]):
    cat_to_expense: dict[Category, list[Expense]] = {}
    for expense in expenses:
        category = await expense.category
        if not cat_to_expense.get(category, None):
            cat_to_expense[category] = [expense]
            continue

        cat_to_expense[category].append(expense)

    return cat_to_expense


@router.message(filters.Command("expenses"))
async def get_categories(message: types.Message):
    user_tz = await UserCRUD.get_tz(message.from_user.id)
    now = datetime.now(user_tz)

    expenses: list = await ExpenseCRUD.filter_by(
        created_at__year=now.year,
        created_at__month=now.month,
        created_at__day=now.day,
        user_id=message.from_user.id
    )

    expenses.sort(key=lambda e: e.category_id)

    cat_to_expenses = await map_cat_to_expense(expenses)

    if not expenses:
        await message.answer(f"🕳 You still don't have any expenses! Create one with " + md.quote('/create_expense'))
        return

    await message.answer(
        **as_list(
            as_section(
                f"🗂 You have {len(expenses)} expenses for today.\n",
                as_list(
                    *[
                        as_marked_section(
                            Bold(cat.name),
                            *[
                                 f"At {expense.created_at.astimezone(user_tz).strftime('%H:%M')} "
                                 f"for {expense.value}BGN"
                                 for expense in expenses
                             ] + [Bold(f"> Category total: {sum([expense.value for expense in expenses])}BGN")]
                        )
                        for cat, expenses in cat_to_expenses.items()
                    ],
                    sep="\n\n"
                ),
            ),
            Text(f"📊 Total for today: {sum([expense.value for expense in expenses])}BGN"),
            sep="\n\n"
        ).as_kwargs()
    )
