# from asyncio import sleep
#
# from aiogram import types
#
#
# async def reply_and_delete(message: types.Message, text: str, interval: int = 5, **kwargs):
#     msg = await message.reply(text, **kwargs)
#
#     await sleep(interval)
#     await msg.delete()
#
#
# async def answer_and_delete(message: types.Message, text: str, interval: int = 5, **kwargs):
#     msg = await message.answer(text, **kwargs)
#
#     await sleep(interval)
#     await msg.delete()