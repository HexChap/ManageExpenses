from _decimal import Decimal

from wrap.core import BasePydantic


class ExpenseSchema(BasePydantic):
    id: int
    user_id: int
    category_id: int
    value: Decimal


class ExpensePayload(BasePydantic):
    category_id: int
    user_id: int
    value: str
