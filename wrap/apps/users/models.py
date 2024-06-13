from tortoise import fields

from wrap.core import AbstractModel


class User(AbstractModel):
    tg_id = fields.CharField(64)
    timezone = fields.CharField(48, null=True)
