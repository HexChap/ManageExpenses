from pydantic import BaseModel

from wrap.core import BasePydantic


class CategorySchema(BasePydantic):
    id: int
    user_id: int | None
    name: str


class CategoryPayload(BaseModel):
    name: str
    user_id: int | None
