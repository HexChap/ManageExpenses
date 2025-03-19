import logging
import re
from asyncio import sleep
from decimal import Decimal

from aiogram import filters, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from wrap.apps.categories import CategoryCRUD, Category
from wrap.apps.expenses import ExpenseCRUD
from wrap.apps.expenses.schemas import ExpensePayload
from wrap.routers.expenses import router
from wrap.routers.expenses.get_today import get_daily

VALUE_REGEX = re.compile(r"^\d{0,10}[\.,]?\d{0,2}$")


class CreateExpense(StatesGroup):
    start = State()
    choosing_category = State()
    set_value = State()
    finish = State()  # So that if qr is scanned it can go straight to finish


@router.message(filters.Command("create_expense"))
@router.message(F.text == "📄 Create income")
@router.callback_query(F.data == "create_expense")
async def create_expense(data: types.Message | types.CallbackQuery, state: FSMContext):
    categories = await CategoryCRUD.filter_by(user_id=data.from_user.id)  # TODO: ReDo with aiogram-dialog?

    if not categories:
        await data.answer(f"🕳 You don't have any categories!")
        return

    builder = ReplyKeyboardBuilder()
    [
        builder.add(types.KeyboardButton(text=category.name))
        for category in categories
    ],
    builder.adjust(2)

    await data.bot.send_message(
        data.from_user.id,
        "🗂 Select category for your expense.",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )

    await state.update_data(categories=categories)
    await state.set_state(CreateExpense.choosing_category)

    if isinstance(data, types.CallbackQuery):
        await data.message.delete()
        await data.answer()


@router.message(CreateExpense.choosing_category)
async def process_category(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cat_matches: list = [
        category
        for category in data["categories"]
        if category.name == message.text
    ]

    if not cat_matches:
        await message.answer("‼️ Please, choose category from the list below.")
        return

    if len(cat_matches) > 1:
        logging.error("Multiple categories found. Aborting " + str(cat_matches))
        return

    category = cat_matches[0]

    if value := data.get("value", None):  # If value is already set (by qr for example)
        if isinstance(value, Decimal):
            await finish_expense_create(message, category, value, state)
            return

    await state.set_data({})
    await state.update_data(category=category)

    await message.answer("💸 Enter the value of the expense.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CreateExpense.set_value)


@router.message(CreateExpense.set_value)
async def process_value(message: types.Message, state: FSMContext):
    if not re.match(VALUE_REGEX, message.text):
        await message.answer(
            "❌ I can't process your input. "
            "Make sure your value is less than 10 billion and has less than 2 decimal places.\n"
            "ℹ️ For example: `12.66`"
        )
        return

    category = (await state.get_data())["category"]
    value = Decimal(message.text.replace(",", "."))

    await finish_expense_create(message, category, value, state)


async def finish_expense_create(message: types.Message, category: Category, value: Decimal, state: FSMContext):
    await ExpenseCRUD.create_by(
        ExpensePayload(
            category_id=category.id,
            user_id=message.from_user.id,
            value=value
        )
    )

    success = await message.answer(
        **Text(
            "✅ Expense in category ", Bold(category.name), f" for {value}BGN created successfully!"
        ).as_kwargs(),
        reply_markup=types.ReplyKeyboardRemove()
    )

    await state.clear()
    await get_daily(message)
    await sleep(5)
    await success.delete()
