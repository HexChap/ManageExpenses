from aiogram import Router, types, filters, md
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Text, Bold, as_list, as_marked_section, as_marked_list, as_section
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from wrap.apps.categories import CategoryCRUD, CategoryPayload

router = Router(name=__name__)


class CreateCategory(StatesGroup):
    choosing_name = State()


class DeleteCategory(StatesGroup):
    choosing_category = State()


@router.message(filters.StateFilter(None), filters.Command("create_category"))
async def create_category(message: types.Message, state: FSMContext):
    await message.answer("🗂 Enter name for the category: ")

    await state.set_state(CreateCategory.choosing_name)


@router.message(filters.StateFilter(CreateCategory.choosing_name))
async def cat_name_chosen(message: types.Message, state: FSMContext):
    if len(message.text) > 32:
        await message.answer("❌ Category name must be shorter than 64 characters.")
        return

    categories = await CategoryCRUD.filter_by(user_id=message.from_user.id)

    if message.text in [category.name for category in categories]:
        await message.answer("‼️ Category with this name already exists!")
        return

    await CategoryCRUD.create_by(
        CategoryPayload(name=message.text, user_id=message.from_user.id)
    )

    await message.answer(
        **Text("✅ Category ", Bold(message.text), " created successfully!").as_kwargs()
    )
    await state.clear()


@router.message(filters.StateFilter(None), filters.Command("delete_category"))
async def delete_category(message: types.Message, state: FSMContext):
    categories = await CategoryCRUD.filter_by(user_id=message.from_user.id)

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
        "🗂 Select a category for deletion.",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )

    await state.update_data(categories=categories)
    await state.set_state(DeleteCategory.choosing_category)


@router.message(filters.StateFilter(DeleteCategory.choosing_category))
async def cat_chosen(message: types.Message, state: FSMContext):
    categories = (await state.get_data())["categories"]

    if message.text not in [category.name for category in categories]:
        await message.answer("‼️ Please, choose category from the list below.")
        return

    await CategoryCRUD.delete_by(name=message.text)

    await message.answer(
        **Text("✅ Category ", Bold(message.text), " deleted successfully!").as_kwargs()
    )
    await state.clear()


@router.message(filters.Command("categories"))
async def get_categories(message: types.Message):
    categories = await CategoryCRUD.filter_by(user_id=message.from_user.id)

    if not categories:
        await message.answer(f"🕳 You don't have any categories! Create one with " + md.quote('/create_category'))
        return

    await message.answer(
        **as_section(
            f"🗂 You have {len(categories)} categories:\n",
            as_marked_list(
                *[Text(category.name) for category in categories],
            )
        ).as_kwargs()
    )
