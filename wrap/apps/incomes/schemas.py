from _decimal import Decimal

from pydantic import BaseModel

from wrap.core import BasePydantic


class IncomeSchema(BasePydantic):
    user_id: int
    value: Decimal


class IncomePayload(BaseModel):
    user_id: int
    value: Decimal
