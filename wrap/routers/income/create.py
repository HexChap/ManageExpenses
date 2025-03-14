import re
from asyncio import sleep
from decimal import Decimal

from aiogram import filters, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Text, Bold

from wrap.apps.expenses import ExpenseCRUD
from wrap.apps.expenses.schemas import ExpensePayload
from wrap.apps.incomes import IncomeCRUD
from wrap.apps.incomes.schemas import IncomePayload
from wrap.core import AMOUNT_REGEX
from wrap.routers.expenses import router
from wrap.routers.expenses.get_today import get_daily


class AddIncome(StatesGroup):
    set_value = State()

@router.message(filters.Command("add_income"))
@router.message(F.text == "💸 Add income")
@router.callback_query(F.data == "add_income")
async def process_category(data: types.Message | types.CallbackQuery, state: FSMContext):
    await data.bot.send_message(
        data.from_user.id,
        "💸 Enter the value of the income.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddIncome.set_value)

    if isinstance(data, types.CallbackQuery):
        await data.message.delete()
        await data.answer()


@router.message(AddIncome.set_value)
async def process_value(message: types.Message, state: FSMContext):
    if not re.match(AMOUNT_REGEX, message.text):
        await message.answer(
            "❌ I can't process your input. "
            "Make sure your value is less than 10 billion and has less than 2 decimal places.\n"
            "ℹ️ For example: `12.66`"
        )
        return

    value = message.text.replace(",", ".")

    income = await IncomeCRUD.create_by(
        IncomePayload(
            user_id=message.from_user.id,
            value=Decimal(value)
        )
    )

    success = await message.answer(
        **Text(
            f"✅ Income for {message.text}BGN created successfully!"
        ).as_kwargs()
    )
    await state.clear()

    await get_daily(message)
    await sleep(5)
    await success.delete()
