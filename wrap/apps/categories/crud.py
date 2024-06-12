from . import Category
from wrap.core import BaseCRUD


class CategoryCRUD(BaseCRUD[Category]):
    model = Category
