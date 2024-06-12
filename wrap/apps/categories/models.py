from tortoise import fields

from wrap.core import AbstractModel


class Category(AbstractModel):
    name = fields.CharField(32)
    user_id = fields.CharField(64, null=True)
