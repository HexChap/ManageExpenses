import asyncio
import importlib
from pathlib import Path
import logging
import os
import sys

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from tortoise import Tortoise

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
        db_url=settings.db_url,
        use_tz=True
    )
    await Tortoise.generate_schemas()


def load_handlers(router_name: str, router_dir: str | Path):
    for module_name in os.listdir(router_dir):
        if module_name.startswith("_"):
            continue

        importlib.import_module(f"{router_name}.{module_name.removesuffix('.py')}")


def include_routers():
    """
    Routers must contain the **router** variable \n
    If router's name starts with "_" it won't be included
    """
    common = importlib.import_module(f"wrap.routers.common")  # Prioritize the cancel handler
    dp.include_router(common.router)

    for module_name in os.listdir(Path("wrap") / "routers"):
        if module_name.startswith("_") or module_name.endswith(".py"):
            continue

        router_path = f"wrap.routers.{module_name}"
        router_module = importlib.import_module(router_path)

        load_handlers(router_path, Path(router_module.__file__).parent)

        dp.include_router(router_module.router)


async def main():
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    await init_database()
    include_routers()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
