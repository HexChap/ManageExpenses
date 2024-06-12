from wrap.apps.expenses import Expense
from wrap.core import BaseCRUD


class ExpenseCRUD(BaseCRUD[Expense]):
    model = Expense
