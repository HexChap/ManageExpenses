from tortoise import fields

from wrap.core import AbstractModel


class Income(AbstractModel):
    # category: fields.ForeignKeyRelation["Category"] = fields.ForeignKeyField(
    #     "models.Category", "expenses"
    # )
    value = fields.DecimalField(10, 2)
    user_id = fields.CharField(max_length=64)

    class Meta:
        table = "incomes"
