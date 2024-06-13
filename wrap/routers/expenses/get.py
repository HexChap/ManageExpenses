from datetime import datetime

import pytz
from aiogram import types, filters, md
from aiogram.utils.formatting import Text, as_marked_list, as_section, as_marked_section, as_list
from tortoise import timezone

from . import router
from wrap.apps.expenses import ExpenseCRUD, Expense
from ...apps.categories import Category


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
    now = timezone.now()

    expenses: list = await ExpenseCRUD.filter_by(
        created_at__year=now.year,
        created_at__month=now.month,
        created_at__day=now.day
    )

    expenses.sort(key=lambda e: e.category_id)

    cat_to_expenses = await map_cat_to_expense(expenses)

    if not expenses:
        await message.answer(f"🕳 You still don't have any expenses! Create one with " + md.quote('/create_expense'))
        return
    print(timezone.localtime(expenses[0].created_at))
    await message.answer(
        **as_section(
            f"🗂 You have {len(expenses)} expenses now.\n",
            as_list(
                *[
                    as_marked_section(
                        cat.name,
                        *[f"At {expense.created_at.strftime('%H:%M')} for {expense.value}BGN" for expense in expenses]
                    )
                    for cat, expenses in cat_to_expenses.items()
                ],
                sep="\n\n"
            )
        ).as_kwargs()
    )
