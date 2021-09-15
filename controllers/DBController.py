from typing import Optional

from data.DBWorker import DBWorker
from entity.dataclass.LotData import LotData
from entity.dataclass.UserData import UserData
from entity.dataclass.CharData import CharData
from entity.enums.Event import Event
from entity.enums.NewLotSessionParam import NewLotSessionParam
from entity.enums.Race import Race
from entity.enums.SearchSessionParam import SearchSessionParam
from entity.enums.Server import Server
from logger.Logger import Logger


class DBController:
    @staticmethod
    def mark_message_as_deleted(message_id: int, chat_id: int) -> bool:
        return DBWorker.remove_message(message_id, chat_id)

    @staticmethod
    def get_messages_to_delete(chat_id: int) -> [int]:
        ids = DBWorker.get_ids_of_messages_to_delete(chat_id)
        if ids is None:
            return []
        return ids

    @staticmethod
    def save_message(message_id: int, chat_id: int) -> bool:
        return DBWorker.save_message_id(chat_id, message_id)

    @staticmethod
    def get_lot(lot_id: int) -> LotData:
        return DBWorker.get_lot(lot_id)

    @staticmethod
    def create_lot(user_id: int) -> bool:
        lot = DBWorker.get_saved_nls_params(user_id)
        if lot is None:
            return False
        result = DBWorker.open_lot(lot.user, lot.char, lot.price, lot.contact_info)
        return result

    @staticmethod
    def get_filtered_lots(user_id: int) -> ([LotData], Event):
        lots = DBWorker.get_filtered_lots(user_id)
        if lots is None:
            return [], Event.db_error
        if not len(lots):
            return [], Event.no_lots_found
        return lots, Event.filtered_lots_found

    @staticmethod
    def update_new_lot_session_params(user_id: int, param: NewLotSessionParam, value) -> bool:
        assert value is not None
        return DBWorker.update_new_lot_session_params(user_id, param, value)

    @staticmethod
    def update_search_session_params(user_id: int, param: SearchSessionParam, value) -> bool:
        assert value is not None
        return DBWorker.update_search_session_params(user_id, param, value)

    @staticmethod
    def wipe_sessions() -> bool:
        result = DBWorker.wipe_sessions()
        if result:
            Logger.debug(f'Sessions has been wiped')
        return result

    @staticmethod
    def register_session(user: UserData) -> bool:
        if not DBWorker.is_session_registered(user.user_id):
            Logger.debug(f'Session for user {user.user_id} has been registered')
        return DBWorker.register_session(user)

    @staticmethod
    def register_new_lot(user: UserData, char: CharData, price: float, contact_info: str) -> bool:
        result = DBWorker.open_lot(user, char, price, contact_info)
        if not result:
            Logger.error(f'Failed to open lot')
        return result

    @staticmethod
    def close_lot(lot_id: int) -> bool:
        result = DBWorker.close_lot(lot_id)
        if not result:
            Logger.error(f'Failed to close lot #{lot_id}')
        return result

    @staticmethod
    def get_lots(server: Server, race: Race) -> [LotData]:
        return [lot for lot in DBWorker.get_all_active_lots()
                if lot.char.race == race and lot.char.server == server]

    @staticmethod
    def get_user_lots(user_id: int) -> [LotData]:
        return DBWorker.get_user_lots(user_id)
