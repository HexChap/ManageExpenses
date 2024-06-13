import pytz
from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from tortoise import timezone

from wrap.routers.misc import router


class ChooseTimezone(StatesGroup):
    continent = State()
    timezone = State()


def get_timezones():
    return_value = {}
    for tz in pytz.common_timezones:
        c = tz.split("/")
        if len(c) > 1:
            if c[0] not in return_value.keys():
                return_value[c[0]] = []
            return_value[c[0]].append(c[1])

        for i in ["GMT"]:
            if i in return_value.keys():
                return_value.pop(i)

    return return_value


def get_continent_keyboard():
    keyboard = ReplyKeyboardBuilder()

    for continent in sorted(get_timezones().keys()):
        keyboard.add(types.KeyboardButton(text=continent))

    keyboard.adjust(4)

    return keyboard


def get_timezone_keyboard(continent: str):
    keyboard = ReplyKeyboardBuilder()

    for timezone in sorted(get_timezones()[continent]):
        keyboard.add(types.KeyboardButton(text=timezone))

    keyboard.adjust(5)

    return keyboard


@router.message(Command("set_timezone"))
async def handle_location(message: types.Message, state: FSMContext):
    await message.answer(
        "🗺 Let's set up your timezone! Select your continent.",
        reply_markup=get_continent_keyboard().as_markup(resize_keyboard=True, one_time_keyboard=True)
    )
    await state.set_state(ChooseTimezone.continent)


@router.message(ChooseTimezone.continent)
async def process_continent(message: types.Message, state: FSMContext):
    if message.text not in get_timezones().keys():
        await message.answer("❌ I can't recognise this continent. Please, choose one from the keyboard")
        return

    await message.answer(
        "⏰ Awesome! Pick your timezone.",
        reply_markup=get_timezone_keyboard(message.text).as_markup(resize_keyboard=True, one_time_keyboard=True)
    )
    await state.update_data(continent=message.text)
    await state.set_state(ChooseTimezone.timezone)


@router.message(ChooseTimezone.timezone)
async def process_continent(message: types.Message, state: FSMContext):
    continent = (await state.get_data()).get("continent")
    if message.text not in get_timezones()[continent]:
        await message.answer("❌ I can't recognise this timezone. Please, choose one from the keyboard")
        return

    await message.answer(
        "✅ Great! Profile's timezone updated!"
    )

    #  pytz.timezone("/".join([continent, message.text]))

    await state.clear()
