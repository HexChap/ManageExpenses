import re

from .bases import AbstractModel, BasePydantic, BaseCRUD

AMOUNT_REGEX = re.compile(r"^\d{0,10}[\.,]?\d{0,2}$")
