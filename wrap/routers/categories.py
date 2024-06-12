from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Text, Bold

from wrap.apps.categories import CategoryCRUD, CategoryPayload

router = Router(name=__name__)


class CreateCategory(StatesGroup):
    choosing_name = State()


@router.message(filters.StateFilter(None), filters.Command("create_category"))
async def create_category(message: types.Message, state: FSMContext):
    await message.answer("🗂 Enter name for the category: ")

    await state.set_state(CreateCategory.choosing_name)


@router.message(filters.StateFilter(CreateCategory.choosing_name))
async def cat_name_chosen(message: types.Message, state: FSMContext):
    if len(message.text) > 32:
        await message.answer("❌ Category name must be shorter than 64 characters.")
        return

    await CategoryCRUD.create_by(
        CategoryPayload(name=message.text, user_id=message.from_user.id)
    )

    await message.answer(
        **Text("✅ Category ", Bold(message.text), " created successfully!").as_kwargs()
    )
