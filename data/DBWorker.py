import datetime
import time
from typing import Optional

from data.db_utils import execute_query, execute_query_with_cursor
from entity.dataclass.CharData import CharData
from entity.dataclass.LotData import LotData
from entity.dataclass.UserData import UserData
from entity.enums.Race import Race
from entity.enums.Server import Server


class DBWorker:
    @staticmethod
    def insert_user(user: UserData) -> bool:
        if DBWorker.__find_user(user) is not None:
            return True
        return execute_query(f'insert into user values ({user.user_id})')

    @staticmethod
    def insert_char(char: CharData) -> bool:
        if DBWorker.__find_char(char) is not None:
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
        return [
            DBWorker.__lot_data_from_tuple(e) for e in execute_query_with_cursor(
                f'select * from lot where date_close is null'
            )
        ]

    @staticmethod
    def open_lot(user: UserData, char: CharData, price: float) -> bool:
        if DBWorker.__find_active_lot(user, char) is not None:
            return True
        return execute_query(
            f'insert into lot values ('
            f'null, '
            f'{DBWorker.__checked_char_id(char)}, '
            f'{DBWorker.__checked_user_id(user)}, '
            f'{time.time()}, '
            f'null, '
            f'{price})'
        )

    @staticmethod
    def close_lot(user: UserData, char: CharData) -> bool:
        lot_id = DBWorker.__find_active_lot(user, char)
        assert lot_id is not None
        return execute_query(f'update lot set date_close = {time.time()} where lot_id = {lot_id}')

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
    def __checked_char_id(char: CharData) -> int:
        if not DBWorker.__find_char(char):
            print(DBWorker.__find_char(char))
            assert DBWorker.insert_char(char)
        return DBWorker.__find_char(char)

    @staticmethod
    def __checked_user_id(user: UserData) -> int:
        if not DBWorker.__find_user(user):
            assert DBWorker.insert_user(user)
        return DBWorker.__find_user(user)

    @staticmethod
    def __user_data_from_tuple(data) -> UserData:
        return UserData(
            user_id=data[0]
        )

    @staticmethod
    def __char_data_from_tuple(data) -> CharData:
        return CharData(
            server=Server[data[1]],
            race=Race[data[2]],
            lvl=data[3],
            char_class=data[4],
            description=data[5],
            heavens=data[6],
            doll=data[7],
            char_id=data[0]
        )

    @staticmethod
    def __lot_data_from_tuple(data) -> LotData:
        char = execute_query_with_cursor(f'select * from character where char_id = {data[1]}')
        user = execute_query_with_cursor(f'select * from user where user_id = {data[2]}')
        assert len(char) > 0 and len(user) > 0
        return LotData(
            char=DBWorker.__char_data_from_tuple(char[0]),
            user=DBWorker.__user_data_from_tuple(user[0]),
            price=data[5],
            date_opened=datetime.datetime.fromtimestamp(data[3]),
            date_closed=datetime.datetime.fromtimestamp(data[4]) if data[4] is not None else None,
            lot_id=data[0]
        )
