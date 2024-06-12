from _decimal import Decimal

from pydantic import BaseModel

from wrap.core import BasePydantic


class ExpenseSchema(BasePydantic):
    user_id: int
    category_id: int
    value: Decimal


class ExpensePayload(BaseModel):
    category_id: int
    user_id: int
    value: Decimal
