from _decimal import Decimal

from pydantic import BaseModel

from wrap.core import BasePydantic


class UserSchema(BasePydantic):
    tg_id: int
    timezone: str


class UserPayload(BaseModel):
    tg_id: int
    timezone: str | None


class UserUpdate(BaseModel):
    timezone: str
