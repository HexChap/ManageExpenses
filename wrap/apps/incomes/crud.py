from . import Income
from wrap.core import BaseCRUD


class IncomeCRUD(BaseCRUD[Income]):
    model = Income
