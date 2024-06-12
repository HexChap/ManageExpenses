import datetime
from typing import Generic, TypeVar

import tortoise
from pydantic import BaseModel
from tortoise import Model, fields
from tortoise.exceptions import DoesNotExist

CRUDModel = TypeVar('CRUDModel', bound=Model)


class AbstractModel(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BasePydantic(BaseModel):
    id: int
    created_at: datetime.datetime


class BaseCRUD(Generic[CRUDModel]):
    model: CRUDModel = CRUDModel

    @classmethod
    async def create_by(cls, payload: BaseModel) -> CRUDModel:
        instance = await cls.model.create(**payload.model_dump())

        return instance

    @classmethod
    async def get_by(cls, **kwargs) -> CRUDModel | None:
        return await cls.model.get_or_none(**kwargs)

    @classmethod
    async def get_all(cls) -> list[CRUDModel]:
        return await cls.model.all()

    @classmethod
    async def filter_by(cls, **kwargs) -> list[CRUDModel] | None:
        try:
            return await cls.model.filter(**kwargs)

        except DoesNotExist as e:
            return None

    @classmethod
    async def update_by(cls, payload: BaseModel | dict, **kwargs) -> CRUDModel:
        instance = await cls.get_by(**kwargs)

        if not instance:
            raise tortoise.exceptions.DoesNotExist

        as_dict = payload.items() if isinstance(payload, dict) else payload.model_dump().items()

        await instance.update_from_dict(
            {
                key: value for key, value in as_dict
                if value is not None
            }
        ).save()
        return instance

    @classmethod
    async def delete_by(cls, **kwargs) -> None:
        instance = await cls.get_by(**kwargs)

        await instance.delete()
