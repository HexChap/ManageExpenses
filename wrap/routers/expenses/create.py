import re
from asyncio import sleep
from decimal import Decimal

from aiogram import filters, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from wrap.apps.categories import CategoryCRUD
from wrap.apps.expenses import ExpenseCRUD
from wrap.apps.expenses.schemas import ExpensePayload
from wrap.routers.expenses import router
from wrap.routers.expenses.get_today import get_daily

VALUE_REGEX = re.compile(r"^\d{0,10}[\.,]?\d{0,2}$")


class CreateExpense(StatesGroup):
    choosing_category = State()
    set_value = State()


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
    categories: list = (await state.get_data())["categories"]

    if message.text not in [category.name for category in categories]:
        await message.answer("‼️ Please, choose category from the list below.")
        return

    await state.set_data({})
    await state.update_data(
        category=[
            category
            for category in categories
            if category.name == message.text
        ][0]
    )

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
    value = message.text.replace(",", ".")

    expense = await ExpenseCRUD.create_by(
        ExpensePayload(
            category_id=category.id,
            user_id=message.from_user.id,
            value=Decimal(value)
        )
    )

    success = await message.answer(
        **Text(
            "✅ Expense in category ", Bold(category.name), f" for {message.text}BGN created successfully!"
        ).as_kwargs()
    )
    await state.clear()

    await get_daily(message)
    await sleep(5)
    await success.delete()
