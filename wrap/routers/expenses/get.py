from datetime import datetime
from io import BytesIO

from aiogram.types import BufferedInputFile
from matplotlib import pyplot as plt

import pytz
from aiogram import types, filters, md
from aiogram.utils.formatting import Text, as_marked_list, as_section, as_marked_section, as_list, Bold, Code
from matplotlib.figure import Figure
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


def create_expenses_pie(cat_to_expenses: dict[Category, list[Expense]]):
    labels = [cat.name for cat in cat_to_expenses.keys()]
    sizes = [sum([expense.value for expense in expenses]) for expenses in cat_to_expenses.values()]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=list(labels), autopct='%1.1f%%')

    buffer = BytesIO()
    fig.savefig(buffer, format="png")

    return buffer


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

    if not expenses:
        await message.answer(f"🕳 You still don't have any expenses for today! Create one with " + md.quote('/create_expense'))
        return

    cat_to_expenses = await map_cat_to_expense(expenses)
    result_buffer = create_expenses_pie(cat_to_expenses)

    result_buffer.seek(0)
    await message.bot.send_photo(
        chat_id=message.from_user.id,
        photo=BufferedInputFile(result_buffer.read(), filename="pie.jpg"),
        caption=as_list(
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
        ).as_html(),
        parse_mode="HTML"
    )
    result_buffer.close()
