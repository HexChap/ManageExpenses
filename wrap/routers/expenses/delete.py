from datetime import datetime

from aiogram import filters, types, md
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from wrap.apps.categories import CategoryCRUD
from wrap.apps.expenses import ExpenseCRUD
from wrap.apps.users import UserCRUD
from wrap.routers.categories import router


class DeleteExpense(StatesGroup):
    expense = State()


@router.message(filters.Command("delete_expense"))
async def delete_expense(message: types.Message, state: FSMContext):
    user_tz = await UserCRUD.get_tz(message.from_user.id)
    now = datetime.now(user_tz)
    expenses = await ExpenseCRUD.filter_by(
        created_at__year=now.year,
        created_at__month=now.month,
        created_at__day=now.day,
        user_id=message.from_user.id
    )

    if not expenses:
        await message.answer(f"🕳 You don't have any expenses! Create one with " + md.quote('/create_expense'))
        return

    builder = ReplyKeyboardBuilder()
    [
        builder.add(types.KeyboardButton(
            text="At " + expense.created_at.astimezone(user_tz).strftime('%H:%M') + f" for {expense.value}BGN"
        ))
        for expense in expenses
     ],
    builder.adjust(3)

    await message.answer(
        "📄 Select an expense for deletion. Only expenses from today are shown.",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )

    await state.update_data(expenses=expenses, user_tz=user_tz)
    await state.set_state(DeleteExpense.expense)


@router.message(filters.StateFilter(DeleteExpense.expense))
async def expense_chosen(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    expense_texts = [
        "At " + expense.created_at.astimezone(state_data["user_tz"]).strftime('%H:%M') + f" for {expense.value}BGN"
        for expense in state_data["expenses"]
    ]
    if message.text not in expense_texts:
        await message.answer("‼️ Please, choose an expense from the list below.")
        return

    await ExpenseCRUD.delete_by(id=state_data["expenses"][expense_texts.index(message.text)].id)

    await message.answer(
        **Text("✅ Category ", Bold(message.text), " deleted successfully!").as_kwargs()
    )
    await state.clear()
