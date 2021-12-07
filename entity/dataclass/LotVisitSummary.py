import datetime

from entity.dataclass.LotData import LotData


class LotVisitSummary:
    def __init__(
            self,
            lot: LotData,
            date_from: datetime.date,
            visits_count: int,
    ):
        self.lot = lot
        self.date_from = date_from
        self.visits_count = visits_count
