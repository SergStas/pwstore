import datetime

from entity.dataclass.CharData import CharData
from entity.dataclass.UserData import UserData


class LotData:
    def __init__(
            self,
            char: CharData,
            user: UserData,
            price: float,
            date_opened: datetime.date,
            date_closed: datetime.date = None,
            lot_id: int = None
    ):
        self.char = char
        self.user = user
        self.price = price
        self.date_opened = date_opened
        self.date_closed = date_closed
        self.lot_id = lot_id
