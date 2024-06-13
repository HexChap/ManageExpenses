import re
from decimal import Decimal

from aiogram import filters, F, types, md
from aiogram.fsm.context import FSMContext

from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.text_decorations import markdown_decoration

from wrap.apps.categories import CategoryCRUD
from wrap.apps.expenses import ExpenseCRUD
from wrap.apps.expenses.schemas import ExpensePayload
from wrap.routers.expenses import router

VALUE_REGEX = re.compile("^\d{1,10}[\.,]?\d{1,2}$")


class CreateExpense(StatesGroup):
    choosing_category = State()
    set_value = State()


@router.message(filters.Command("create_expense"))
@router.message(F.text == "📄 Create expense")
async def create_expense(message: types.Message, state: FSMContext):
    categories = await CategoryCRUD.filter_by(user_id=message.from_user.id)  # TODO: ReDo with aiogram-dialog?

    if not categories:
        await message.answer(f"🕳 You don't have any categories! Create one with " + md.quote('/create_category'))
        return

    builder = ReplyKeyboardBuilder()
    [
        builder.add(types.KeyboardButton(text=category.name))
        for category in categories
    ],
    builder.adjust(2)

    await message.answer(
        "🗂 Select category for your expense.",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )

    await state.update_data(categories=categories)
    await state.set_state(CreateExpense.choosing_category)


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

    await message.answer("💸 Enter the value of the expense.")
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

    await message.answer(
        **Text(
            "✅ Expense in category ", Bold(category.name), f" for {message.text} created successfully!"
        ).as_kwargs()
    )
    await state.clear()
