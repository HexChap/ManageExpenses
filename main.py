import asyncio
import os
from pathlib import Path

from tortoise import Tortoise

from wrap.core import settings


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


asyncio.run(init_database())
