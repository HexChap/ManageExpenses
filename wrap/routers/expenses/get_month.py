import math
from _decimal import Decimal
from calendar import monthrange
from datetime import datetime, timezone
from io import BytesIO

import numpy as np
import pytz
from aiogram import types, md, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from aiogram.utils.formatting import Text, as_list, as_section, as_marked_section, Bold
from matplotlib import pyplot as plt
from tortoise.timezone import is_aware

from wrap.apps.expenses import ExpenseCRUD, Expense
from wrap.apps.users import UserCRUD
from . import router
from ._keyboards import get_daily_kb
from .get_today import map_cat_to_expense
from ...apps.categories import Category, CategoryCRUD


async def create_expenses_bar(
        expenses: list[Expense],
        cat_ids: list[int],
        days: int,
        user_tz: pytz.tzinfo
):
    cat_to_each_day_total = {cat_id: [0 for _ in range(days)] for cat_id in cat_ids}

    ind = np.arange(days)
    fig, ax = plt.subplots(figsize=(14, 8))
    bars = []
    labels = []

    for expense in expenses:
        day = expense.created_at.astimezone(user_tz).day
        cat_to_each_day_total[expense.category_id][day-1] += float(expense.value)

    for i, cat_id in enumerate(cat_ids):
        bottom = cat_to_each_day_total[cat_ids[i-1]] if i > 0 else None

        labels.append((await CategoryCRUD.get_by(id=cat_id)).name)
        bars.append(plt.bar(ind, cat_to_each_day_total[cat_id], bottom=bottom))

    y_lim = ax.get_ylim()[1]
    plt.ylim(0, math.ceil(y_lim / 10) * 10)  # unfix the highest bar from the top

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

    expenses: list = await ExpenseCRUD.model.filter(
        created_at__year=now.year,
        created_at__month=now.month,
        user_id=tg_id
    ).order_by("created_at")
    cat_ids = await CategoryCRUD.model.filter(user_id=tg_id).values_list("id", flat=True)

    if not expenses:
        await callback.answer(
            f"🕳 You still don't have any expenses for this month!"
        )
        return

    cat_to_expenses = await map_cat_to_expense(expenses)
    cat_to_expenses = {
        cat: sorted(expenses, key=lambda e: e.created_at.day)
        for cat, expenses in cat_to_expenses.items()
    }

    result_buffer = await create_expenses_bar(
        expenses,
        cat_ids,
        monthrange(now.year, now.month)[1],
        user_tz
    )

    result_buffer.seek(0)

    await message.delete()
    await message.bot.send_photo(
        tg_id,
        BufferedInputFile(result_buffer.read(), filename="pie.jpg"),
        caption=as_list(
            as_section(
                f"🗂 You have {len(expenses)} expenses for the month.\n",
                as_list(
                    *[
                        as_marked_section(
                            Bold(cat.name),
                            Text(f"> Category total: {sum([expense.value for expense in expenses])}BGN")
                        )
                        for cat, expenses in cat_to_expenses.items()
                    ],
                    sep="\n\n"
                ),
            ),
            Text(f"📊 Total for the month: {sum([expense.value for expense in expenses])}BGN"),
            sep="\n\n"
        ).as_html(),
        reply_markup=get_daily_kb(),
        parse_mode="HTML"
    )

    await callback.answer()
