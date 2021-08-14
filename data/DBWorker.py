import datetime
import time
from typing import Optional

from data.db_utils import execute_query, execute_query_with_cursor
from entity.dataclass.CharData import CharData
from entity.dataclass.LotData import LotData
from entity.dataclass.UserData import UserData
from entity.enums.Race import Race
from entity.enums.Server import Server
from logger.Logger import Logger


class DBWorker:
    @staticmethod
    def register_session(user_id: int) -> bool:
        if DBWorker.is_session_registered(user_id):
            Logger.error(f'Failed to register session for user #{user_id} - session is already registered')
            return False
        return execute_query(f'insert into session values (null, {user_id}, {time.time()})')

    @staticmethod
    def is_session_registered(user_id: int) -> bool:
        return len(execute_query_with_cursor(f'select * from session where user_id = {user_id}')) > 0

    @staticmethod
    def wipe_sessions() -> bool:
        result = execute_query('delete from session where true')
        if result:
            Logger.debug(f'Sessions has been wiped')
        return result

    @staticmethod
    def insert_user(user: UserData) -> bool:
        if DBWorker.__find_user(user) is not None:
            return True
        result = execute_query(f'insert into user values ({user.user_id})')
        if result:
            Logger.debug(f'New user has been registered, id = {user.user_id}')
        return result

    @staticmethod
    def insert_char(char: CharData) -> bool:
        if char.char_id is not None and char.char_id in \
                [e[0] for e in execute_query_with_cursor('select char_id from character')]:
            return True
        return execute_query(
            f'insert into character values ('
            f'null, '
            f'\'{char.server.name}\', '
            f'\'{char.race.name}\', '
            f'{char.lvl}, '
            f'\'{char.char_class}\', '
            f'\'{char.description}\', '
            f'\'{char.heavens}\','
            f'\'{char.doll}\')'
        )

    @staticmethod
    def get_all_active_lots() -> [LotData]:
        return [converted for converted in [
            DBWorker.__lot_data_from_tuple(e) for e in execute_query_with_cursor(
                f'select * from lot where date_close is null'
            )] if converted is not None]

    @staticmethod
    def open_lot(user: UserData, char: CharData, price: float, contact: str) -> bool:
        if DBWorker.__is_lot_already_opened(user, char):
            Logger.error(f'Lot is already opened')
            return False
        return execute_query(
            f'insert into lot values ('
            f'null, '
            f'{DBWorker.__checked_char_id(char)}, '
            f'{DBWorker.__checked_user_id(user)}, '
            f'{time.time()}, '
            f'null, '
            f'{price},'
            f'\'{contact}\')'
        )

    @staticmethod
    def close_lot(lot: LotData) -> bool:
        try:
            assert lot.lot_id is not None and lot.date_closed is None
            return execute_query(f'update lot set date_close = {time.time()} where lot_id = {lot.lot_id}')
        except Exception as e:
            Logger.error(f'Failed to close lot with id = {lot.lot_id}:\n\t\t\t{e}')
            return False

    @staticmethod
    def get_user_lots(user: UserData):
        return [converted for converted in [DBWorker.__lot_data_from_tuple(e) for e in
                execute_query_with_cursor(
                    f'select * from lot where user_id = {user.user_id} and date_close is not null'
                )] if converted is not None]

    @staticmethod
    def __is_lot_already_opened(user: UserData, char: CharData) -> bool:
        if char.char_id is None:
            return False
        return len(execute_query_with_cursor(
            f'select * from lot where '
            f'user_id = {user.user_id} and '
            f'char_id = {char.char_id}'
        )) > 0

    @staticmethod
    def __find_active_lot(user: UserData, char: CharData) -> Optional[int]:
        try:
            char_id = DBWorker.__find_char(char)
            user_id = DBWorker.__find_user(user)
            assert char_id is not None and user_id is not None
            return int(execute_query_with_cursor(
                f'select * from lot where '
                f'user_id = {user_id} and '
                f'char_id = {char_id} and '
                f'date_close is null'
            )[0][0])
        except Exception:
            return None

    @staticmethod
    def __find_char(char: CharData) -> Optional[int]:
        try:
            return execute_query_with_cursor(
                f'select * from character where '
                f'server = \'{char.server.name}\' and '
                f'race = \'{char.race.name}\' and '
                f'lvl = {char.lvl} and '
                f'class = \'{char.char_class}\' and '
                f'description = \'{char.description}\' and '
                f'heavens = \'{char.heavens}\' and '
                f'doll = \'{char.doll}\''
            )[0][0]
        except Exception:
            return None

    @staticmethod
    def __find_user(user: UserData) -> Optional[int]:
        try:
            return execute_query_with_cursor(
                f'select * from user where '
                f'user_id = {user.user_id}'
            )[0][0]
        except Exception:
            return None

    @staticmethod
    def __checked_char_id(char: CharData) -> Optional[int]:
        try:
            if not DBWorker.__find_char(char):
                assert DBWorker.insert_char(char)
            return DBWorker.__find_char(char)
        except Exception as e:
            Logger.error(f'Failed to get character id:\n\t\t\t{e}')
            return None

    @staticmethod
    def __checked_user_id(user: UserData) -> int:
        if not DBWorker.__find_user(user):
            assert DBWorker.insert_user(user)
        return DBWorker.__find_user(user)

    @staticmethod
    def __user_data_from_tuple(data) -> UserData:
        return DBWorker.__handle_error(
            lambda:
                UserData(
                    user_id=data[0]
                ),
            'Failed to load user info'
        )

    @staticmethod
    def __char_data_from_tuple(data) -> Optional[CharData]:
        return DBWorker.__handle_error(
            lambda:
                CharData(
                    server=Server[data[1]],
                    race=Race[data[2]],
                    lvl=data[3],
                    char_class=data[4],
                    description=data[5],
                    heavens=data[6],
                    doll=data[7],
                    char_id=data[0]
                ),
            'Failed to load character info'
        )

    @staticmethod
    def __lot_data_from_tuple(data) -> Optional[LotData]:
        try:
            char = DBWorker.__char_data_from_tuple(
                execute_query_with_cursor(f'select * from character where char_id = {data[1]}')[0]
            )
            user = DBWorker.__user_data_from_tuple(
                execute_query_with_cursor(f'select * from user where user_id = {data[2]}')[0]
            )
            assert char is not None and user is not None
            return LotData(
                char=char,
                user=user,
                price=data[5],
                date_opened=datetime.datetime.fromtimestamp(data[3]),
                date_closed=datetime.datetime.fromtimestamp(data[4]) if data[4] is not None else None,
                lot_id=data[0],
                contact_info=data[6]
            )
        except Exception as e:
            Logger.error(f'Failed to load data lot info:\n\t\t\t{e}')
            return None

    @staticmethod
    def __handle_error(f, error_message: str = 'Failed to perform operation'):
        try:
            return f()
        except Exception as e:
            Logger.error(f'{error_message}:\n\t\t\t{e}')
            return None
