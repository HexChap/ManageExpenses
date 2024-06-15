import math
from calendar import monthrange
from datetime import datetime
from io import BytesIO

import numpy
import numpy as np
from _decimal import Decimal
from aiogram import types, filters, md, F
from aiogram.types import BufferedInputFile, InputMediaPhoto
from aiogram.utils.formatting import Text, as_section, as_marked_section, as_list, Bold
from matplotlib import pyplot as plt

from wrap.apps.expenses import ExpenseCRUD, Expense
from wrap.apps.users import UserCRUD
from . import router
from .get_today import map_cat_to_expense, create_expenses_pie
from ...apps.categories import Category


def get_expense_values(expenses: list[Expense]) -> list[Decimal]:
    return [expense.value for expense in expenses]


async def map_cat_to_total(expenses: list[Expense]):
    cat_to_total: dict[Category, Decimal] = {}
    for expense in expenses:
        category = await expense.category
        if not cat_to_total.get(category, None):
            cat_to_total[category] = expense.value
            continue

        cat_to_total[category] += expense.value

    return cat_to_total


async def get_expenses_each_day(expenses: list[Expense], days: int) -> list[list[Expense]]:
    result = [[] for i in range(days)]

    for i, expense in enumerate(expenses):
        expense = await expense

        result[expense.created_at.day-1].append(expense)

    return result


async def get_cat_to_expense_each_day(
        expenses: list[Expense],
        days: int
) -> list[dict[Category, list[Expense]]]:
    expenses_each_day = await get_expenses_each_day(expenses, days)
    result = [dict()]*days

    for i, expenses in enumerate(expenses_each_day):
        mapped = await map_cat_to_expense(expenses)

        result[i] = mapped

    return result


async def create_expenses_bar(
        expenses: list[Expense],
        days: int
):
    cat_to_expense_each_day = await get_cat_to_expense_each_day(expenses, days)

    ind = np.arange(days)
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 8))
    bars = []
    labels = set()
    each_cat_total_each_day = [[] for i in range(days)]

    for i, cat_to_expenses in enumerate(cat_to_expense_each_day):
        [labels.add(cat.name) for cat in cat_to_expenses.keys()]

        for j, (cat, expenses) in enumerate(cat_to_expenses.items()):
            each_cat_total_each_day[i].append(
                numpy.float64(sum(get_expense_values(expenses)))
            )

    max_cat_count = max(len(day) for day in each_cat_total_each_day)
    each_cat_each_day_total = [[] for i in range(max_cat_count)]

    for cat_index in range(max_cat_count):
        for j in range(days):
            each_cat_each_day_total[cat_index].append(
                each_cat_total_each_day[j][cat_index]
                if len(each_cat_total_each_day[j]) - 1 >= cat_index
                else 0
            )

    for i, cat_each_day_total in enumerate(each_cat_each_day_total):
        bottom = None if i == 0 else each_cat_each_day_total[i-1]
        bars.append(
            plt.bar(ind, cat_each_day_total, bottom=bottom)
        )

    ylim = ax.get_ylim()[1]
    plt.ylim(0, math.ceil(ylim / 10) * 10)  # unfix highest bar from the top

    plt.title('Amount spend every day by category')
    plt.ylabel('Amount')

    plt.xticks(ind, tuple(range(1, days+1)))
    plt.legend(
        tuple(bar[0] for bar in bars),
        labels
    )

    buffer = BytesIO()
    fig.savefig(buffer, format="png")

    return buffer


@router.callback_query(F.data == "get_monthly")
async def get_monthly_stat(callback: types.CallbackQuery):
    tg_id = callback.from_user.id
    message = callback.message
    user_tz = await UserCRUD.get_tz(tg_id)
    now = datetime.now(user_tz)

    expenses: list = await ExpenseCRUD.filter_by(
        created_at__year=now.year,
        created_at__month=now.month,
        user_id=tg_id
    )

    if not expenses:
        await message.answer(
            f"🕳 You still don't have any expenses for this month! Create one with " +
            md.quote('/create_expense')
        )
        await message.delete()
        await callback.answer()
        return

    cat_to_expenses = await map_cat_to_expense(expenses)
    result_buffer = await create_expenses_bar(expenses, monthrange(now.year, now.month)[1])

    result_buffer.seek(0)
    await message.edit_media(
        media=InputMediaPhoto(media=BufferedInputFile(result_buffer.read(), filename="pie.jpg"))
    )
    await message.edit_caption(
        caption=Text(sum([expense.value for expense in expenses])).as_html(),
        parse_mode="HTML"
    )

    await callback.answer()
