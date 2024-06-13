from aiogram import types, filters, md
from aiogram.utils.formatting import Text, as_marked_list, as_section

from wrap.apps.categories import CategoryCRUD
from . import router


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
