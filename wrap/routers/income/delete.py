from asyncio import sleep
from datetime import datetime

from aiogram import filters, types, md, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from wrap.apps.categories import CategoryCRUD
from wrap.apps.expenses import ExpenseCRUD
from wrap.apps.incomes import IncomeCRUD
from wrap.apps.users import UserCRUD
from wrap.routers.categories import router
from wrap.routers.expenses.get_today import get_daily


class DeleteIncome(StatesGroup):
    income = State()


@router.message(filters.Command("delete_income"))
@router.callback_query(F.data == "delete_income")
async def delete_income(context: types.Message | types.CallbackQuery, state: FSMContext):
    user_tz = await UserCRUD.get_tz(context.from_user.id)
    now = datetime.now(user_tz)
    incomes = await IncomeCRUD.filter_by(
        created_at__year=now.year,
        created_at__month=now.month,
        created_at__day=now.day,
        user_id=context.from_user.id
    )

    if not incomes:
        await context.answer(f"🕳 You still don't have any incomes!")
        return

    builder = ReplyKeyboardBuilder()
    [
        builder.add(types.KeyboardButton(
            text="At " + income.created_at.astimezone(user_tz).strftime('%H:%M') + f" for {income.value}BGN"
        ))
        for income in incomes
     ],
    builder.adjust(3)

    await context.bot.send_message(
        context.from_user.id,
        "📄 Select an income for deletion. Only incomes from today are shown.",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )

    await state.update_data(incomes=incomes, user_tz=user_tz)
    await state.set_state(DeleteIncome.income)

    if isinstance(context, types.CallbackQuery):
        await context.message.delete()
        await context.answer()


@router.message(filters.StateFilter(DeleteIncome.income))
async def income_chosen(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    income_texts = [
        "At " + income.created_at.astimezone(state_data["user_tz"]).strftime('%H:%M') + f" for {income.value}BGN"
        for income in state_data["incomes"]
    ]
    if message.text not in income_texts:
        await message.answer("‼️ Please, choose an income from the list below.")
        return

    await IncomeCRUD.delete_by(id=state_data["incomes"][income_texts.index(message.text)].id)

    success = await message.answer(
        **Text("✅ Income ", Bold(message.text[:1].lower() + message.text[1:]), " deleted successfully!").as_kwargs(),
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.clear()

    await get_daily(message)
    await sleep(5)
    await success.delete()
