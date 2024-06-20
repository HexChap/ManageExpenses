from asyncio import sleep
from datetime import datetime

from aiogram import filters, types, md, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from wrap.apps.categories import CategoryCRUD
from wrap.apps.expenses import ExpenseCRUD
from wrap.apps.users import UserCRUD
from wrap.routers.categories import router
from wrap.routers.expenses.get_today import get_daily


class DeleteExpense(StatesGroup):
    expense = State()


@router.message(filters.Command("delete_expense"))
@router.callback_query(F.data == "delete_expense")
async def delete_expense(context: types.Message | types.CallbackQuery, state: FSMContext):
    user_tz = await UserCRUD.get_tz(context.from_user.id)
    now = datetime.now(user_tz)
    expenses = await ExpenseCRUD.filter_by(
        created_at__year=now.year,
        created_at__month=now.month,
        created_at__day=now.day,
        user_id=context.from_user.id
    )

    if not expenses:
        await context.answer(f"🕳 You still don't have any expenses!")
        return

    builder = ReplyKeyboardBuilder()
    [
        builder.add(types.KeyboardButton(
            text="At " + expense.created_at.astimezone(user_tz).strftime('%H:%M') + f" for {expense.value}BGN"
        ))
        for expense in expenses
     ],
    builder.adjust(3)

    await context.bot.send_message(
        context.from_user.id,
        "📄 Select an expense for deletion. Only expenses from today are shown.",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )

    await state.update_data(expenses=expenses, user_tz=user_tz)
    await state.set_state(DeleteExpense.expense)

    if isinstance(context, types.CallbackQuery):
        await context.message.delete()
        await context.answer()


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

    success = await message.answer(
        **Text("✅ Category ", Bold(message.text), " deleted successfully!").as_kwargs(),
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.clear()

    await get_daily(message)
    await sleep(5)
    await success.delete()
