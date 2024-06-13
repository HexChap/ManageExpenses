import pytz

from wrap.apps.expenses import Expense
from wrap.apps.users import User
from wrap.core import BaseCRUD


class UserCRUD(BaseCRUD[User]):
    model = User

    @classmethod
    async def get_tz(cls, tg_id: int | str):
        user = await UserCRUD.get_by(tg_id=tg_id)

        return pytz.timezone(user.timezone) if user else pytz.utc

