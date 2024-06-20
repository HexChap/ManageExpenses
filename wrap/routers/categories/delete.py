from asyncio import sleep

from aiogram import filters, types, md, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.text_decorations import markdown_decoration

from wrap.apps.categories import CategoryCRUD
from wrap.routers.categories import router
from wrap.routers.expenses.get_today import get_daily


class DeleteCategory(StatesGroup):
    choosing_category = State()


@router.message(filters.StateFilter(None), filters.Command("delete_category"))
@router.callback_query(F.data == "delete_category")
async def delete_category(context: types.Message | types.CallbackQuery, state: FSMContext):
    categories = await CategoryCRUD.filter_by(user_id=context.from_user.id)

    if not categories:
        await context.answer(f"🕳 You don't have any categories!")
        return

    builder = ReplyKeyboardBuilder()
    [
        builder.add(types.KeyboardButton(text=category.name))
        for category in categories
     ],
    builder.adjust(2)

    await context.bot.send_message(
        context.from_user.id,
        "🗂 Select a category for deletion.",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )

    await state.update_data(categories=categories)
    await state.set_state(DeleteCategory.choosing_category)

    if isinstance(context, types.CallbackQuery):
        await context.message.delete()
        await context.answer()


@router.message(filters.StateFilter(DeleteCategory.choosing_category))
async def cat_chosen(message: types.Message, state: FSMContext):
    categories = (await state.get_data())["categories"]

    if message.text not in [category.name for category in categories]:
        await message.answer("‼️ Please, choose category from the list below.")
        return

    await CategoryCRUD.delete_by(name=message.text, user_id=message.from_user.id)

    success = await message.answer(
        **Text("✅ Category ", Bold(message.text), " deleted successfully!").as_kwargs()
    )
    await state.clear()

    await get_daily(message)
    await sleep(5)
    await success.delete()
