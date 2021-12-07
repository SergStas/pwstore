import datetime

from entity.dataclass.LotData import LotData


class LotVisitData:
    def __init__(
            self,
            lot: LotData,
            visit_date: datetime.date,
    ):
        self.lot = lot
        self.visit_date = visit_date
