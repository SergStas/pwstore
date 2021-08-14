from data.DBWorker import DBWorker
from entity.dataclass.LotData import LotData
from entity.dataclass.UserData import UserData
from entity.dataclass.CharData import CharData
from entity.enums.Race import Race
from entity.enums.Server import Server
from logger.Logger import Logger


class DBController:
    @staticmethod
    def register_new_lot(user: UserData, char: CharData, price: float, contact_info: str) -> bool:
        result = DBWorker.open_lot(user, char, price, contact_info)
        if not result:
            Logger.error(f'Failed to open lot')
        return result

    @staticmethod
    def close_lot(lot: LotData) -> bool:
        result = DBWorker.close_lot(lot)
        if not result:
            Logger.error(f'Failed to close lot')
        return result

    @staticmethod
    def get_lots(server: Server, race: Race) -> [LotData]:
        return [lot for lot in DBWorker.get_all_active_lots()
                if lot.char.race == race and lot.char.server == server]

    @staticmethod
    def get_user_lots(user: UserData) -> [LotData]:
        return DBWorker.get_user_lots(user)
