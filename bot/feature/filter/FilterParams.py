class FilterParams:
    def __init__(
            self,
            min_lvl: int = None,
            max_lvl: int = None,
            min_price: int = None,
            max_price: int = None,
    ):
        self.min_lvl = min_lvl
        self.max_lvl = max_lvl
        self.min_price = min_price
        self.max_price = max_price
