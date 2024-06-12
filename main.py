import asyncio
import importlib
import os
from pathlib import Path

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from tortoise import Tortoise
from aiogram import Dispatcher, Bot

from wrap.core import settings

dp = Dispatcher()


async def init_database():
    models = [
        f'wrap.apps.{app_dir}.models'
        for app_dir in os.listdir(Path("wrap") / "apps")
        if not app_dir.startswith("_")
    ]

    await Tortoise.init(
        modules={"models": models},
        db_url=settings.db_url
    )
    await Tortoise.generate_schemas()


def include_routers():
    """
    Routers must contain the **router** variable \n
    If router's name starts with "_" it won't be included
    """
    for module_name in os.listdir(Path("wrap") / "routers"):
        if module_name.startswith("_") or not module_name.endswith(".py"):
            continue

        module = importlib.import_module(f"wrap.routers.{module_name.removesuffix('.py')}")

        dp.include_router(module.router)


async def main():
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

    await init_database()
    include_routers()
    await dp.start_polling(bot)

asyncio.run(main())
