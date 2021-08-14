from data.DBWorker import DBWorker
from entity.dataclass.LotData import LotData
from entity.dataclass.UserData import UserData
from entity.dataclass.CharData import CharData
from entity.enums.Race import Race
from entity.enums.Server import Server


class DBController:
    @staticmethod
    def register_new_lot(user: UserData, char: CharData, price: float, contact_info: str) -> bool:
        return DBWorker.open_lot(user, char, price, contact_info)

    @staticmethod
    def close_lot(lot: LotData) -> bool:
        return DBWorker.close_lot(lot)

    @staticmethod
    def get__lots(server: Server, race: Race) -> [LotData]:
        return [lot for lot in DBWorker.get_all_active_lots()
                if lot.char.race == race and lot.char.server == server]

    @staticmethod
    def get_user_lots(user: UserData) -> [LotData]:
        return DBWorker.get_user_lots(user)
