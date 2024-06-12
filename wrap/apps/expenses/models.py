from typing import TYPE_CHECKING

from tortoise import fields

from wrap.core import AbstractModel

if TYPE_CHECKING:
    from wrap.apps.categories import Category


class Expense(AbstractModel):
    category: fields.ForeignKeyRelation["Category"] = fields.ForeignKeyField(
        "models.Category", "expenses"
    )
    value = fields.DecimalField(10, 2)
    user_id = fields.CharField(max_length=64)
