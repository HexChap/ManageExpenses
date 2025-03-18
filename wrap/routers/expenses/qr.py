from asyncio import sleep
from decimal import Decimal
from typing import BinaryIO

from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext

from . import router
from .create import CreateExpense, create_expense
from .get_today import get_daily
from ...utils import detect_qr_total


@router.message(F.photo)
async def process_qr(message: types.Message, state: FSMContext, bot: Bot):
    image: BinaryIO = await bot.download(message.photo[-2])

    if not (total := detect_qr_total(image)):  # Retrying with better quality, in case if not detected
        await message.answer("🤔 Retrying...")

        image = await bot.download(message.photo[-1])
        total = detect_qr_total(image)

    if total:
        await state.update_data(value=Decimal(total))
        await create_expense(message, state)
        return


    msg = await message.reply(
        "❌ Couldn't detect the QR. Make sure your receipt has one, and that it's clearly visible."
    )

    await get_daily(message)
    await sleep(5)
    await msg.delete()



