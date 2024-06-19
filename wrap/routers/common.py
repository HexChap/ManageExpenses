from aiogram import Router, F, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.utils.formatting import Text

router = Router(name=__name__)


@router.message(filters.StateFilter(None), filters.Command("cancel"))
@router.message(default_state, F.text.lower() == "cancel")
async def cmd_cancel_no_state(message: types.Message, state: FSMContext):
    await state.set_data({})
    await message.answer(
        text="🤔 Nothing to cancel",
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(filters.Command(commands=["cancel"]))
@router.message(F.text.lower() == "cancel")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="✅ Action canceled",
        reply_markup=types.ReplyKeyboardRemove()
    )
