from datetime import datetime
from io import BytesIO

from aiogram import types, filters, md, F
from aiogram.types import BufferedInputFile
from aiogram.utils.formatting import Text, as_section, as_marked_section, as_list, Bold
from matplotlib import pyplot as plt

from wrap.apps.expenses import ExpenseCRUD, Expense
from . import router
from ._keyboards import get_start_kb
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


@router.message(filters.Command(commands=["expenses", "start"]))
@router.callback_query(F.data == "get_daily")
@router.callback_query(F.data == "start")
async def get_daily(context: types.Message | types.CallbackQuery):
    if isinstance(context, types.CallbackQuery):
        is_start = context.data == "start"
    else:
        is_start = context.text == "/start"

    user_tz = await UserCRUD.get_tz(context.from_user.id)
    now = datetime.now(user_tz)

    expenses: list = await ExpenseCRUD.model.filter(
        created_at__year=now.year,
        created_at__month=now.month,
        created_at__day=now.day,
        user_id=context.from_user.id
    ).order_by("category_id")

    if not expenses:
        await context.bot.send_message(
            context.from_user.id,
            Text(f"🕳 You still don't have any expenses for today!").as_html(),
            reply_markup=get_start_kb(),
            parse_mode="HTML"
        )
    else:
        cat_to_expenses = await map_cat_to_expense(expenses)
        result_buffer = create_expenses_pie(cat_to_expenses)

        result_buffer.seek(0)
        await context.bot.send_photo(
            chat_id=context.from_user.id,
            photo=BufferedInputFile(result_buffer.read(), filename="pie.jpg"),
            caption=as_list(
                Text(f"👋 Greetings, {context.from_user.first_name}!") if is_start else Text(),
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
                Text(f"📊 Total for today: {sum([expense.value for expense in expenses])}BGN\n"),
                sep="\n"
            ).as_html(),
            reply_markup=get_start_kb(),
            parse_mode="HTML"
        )
        result_buffer.close()

    if isinstance(context, types.CallbackQuery):
        await context.message.delete()
        await context.answer()
