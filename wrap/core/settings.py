from dataclasses import dataclass
from os import environ

db_url = environ["DB_URL"]
bot_token = environ["BOT_TOKEN"]
drop_pending = environ.get("DROP_PENDING_UPDATES", False)
