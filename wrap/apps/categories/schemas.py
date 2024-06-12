from wrap.core import BasePydantic


class CategorySchema(BasePydantic):
    id: int
    user_id: int | None
    name: str


class CategoryPayload(BasePydantic):
    name: str
    user_id: int | None
