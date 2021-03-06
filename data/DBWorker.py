import datetime
import time
from typing import Optional

from bot.feature.filter.FilterParams import FilterParams
from data.db_utils import execute_query, execute_query_with_cursor
from entity.dataclass.CharData import CharData
from entity.dataclass.LotData import LotData
from entity.dataclass.LotVisitData import LotVisitData
from entity.dataclass.UserData import UserData
from entity.enums.NewLotSessionParam import NewLotSessionParam
from entity.enums.Race import Race
from entity.enums.SearchSessionParam import SearchSessionParam
from entity.enums.Server import Server
from logger.Logger import Logger


class DBWorker:  # TODO: assertion error handling
    @staticmethod
    def get_filter_params(user_id: int) -> FilterParams:
        if user_id is not None and \
                user_id in [e[0] for e in execute_query_with_cursor('select user_id from user')]:
            data = execute_query_with_cursor(
                f'select * from search_session where session_id = {DBWorker.__get_session_for_user(user_id)}'
            )[0]
            return FilterParams(min_lvl=data[3], max_lvl=data[4], min_price=data[5], max_price=data[6])

    @staticmethod
    def get_visit_data_of_lot(lot_id: int) -> [LotVisitData]:
        return [DBWorker.__lot_visit_data_from_tuple(e)
                for e in execute_query_with_cursor(
                    f'select * from lot_visits where lot_id = {lot_id}'
                )]

    @staticmethod
    def add_visit_event(lot_id: int, visitor_id: int):
        if visitor_id is not None and \
                visitor_id in [e[0] for e in execute_query_with_cursor('select user_id from user')] and \
                lot_id is not None and \
                lot_id in [e[0] for e in execute_query_with_cursor('select * from lot')]:
            execute_query(
                f'insert into lot_visits values ('
                f'null,'
                f'{lot_id}, '
                f'{time.time()},'
                f'{visitor_id})'
            )

    @staticmethod
    def is_fav(lot_id: int, user_id: int):
        lots = [e.lot_id for e in DBWorker.get_favs(user_id)]
        return lot_id in lots

    @staticmethod
    def remove_from_favs(user_id: int, lot_id: int):
        execute_query(f'delete from favs where lot_id = {lot_id} and user_id = {user_id}')

    @staticmethod
    def get_favs(user_id: int) -> [LotData]:
        return [converted for converted in
                [DBWorker.__lot_data_from_tuple(execute_query_with_cursor(
                    f'select * from lot where lot_id = {e[2]}'
                )[0]) for e in
                 execute_query_with_cursor(
                     f'select * from favs where user_id = {user_id}'
                 )
                 ] if converted is not None
                ]

    @staticmethod
    def add_to_favs(user_id: int, lot_id: int):
        if DBWorker.is_fav(lot_id, user_id):
            return
        if user_id is not None and \
                user_id in [e[0] for e in execute_query_with_cursor('select user_id from user')] and \
                lot_id is not None and \
                lot_id in [e[0] for e in execute_query_with_cursor('select * from lot')]:
            execute_query(
                f'insert into favs values ('
                f'null,'
                f'{user_id}, '
                f'{lot_id})'
            )

    @staticmethod
    def get_ids_of_messages_to_delete(chat_id: int) -> Optional[list]:
        try:
            return [e[0] for e in execute_query_with_cursor(
                f'select message_id from message_history where chat_id = {chat_id} and not is_deleted and not is_pinned'
            )]
        except Exception as e:
            Logger.error(f'Failed to get messages from chat #{chat_id}:\n\t\t\t{e}')
            return None

    @staticmethod
    def save_message_id(chat_id: int, message_id: int) -> bool:
        result = execute_query(
            f'insert into message_history values({message_id}, {chat_id}, false, false)'
        )
        Logger.fork_log(
            result,
            f'Message #{message_id} saved successfully',
            f'An error has occurred during saving message #{message_id}'
        )
        return result

    @staticmethod
    def pin_message(message_id: int, chat_id: int, flag: bool) -> bool:
        if not DBWorker.__does_message_exist(message_id, chat_id):
            Logger.error(f'Failed to pin message #{message_id}: message not found')
            return False
        result = execute_query(
            f'update message_history set is_pinned = {flag} where message_id = {message_id} and chat_id = {chat_id}'
        )
        Logger.fork_log(
            result,
            f'Message #{message_id} pinned {"on" if flag else "off"} successfully',
            f'Failed to pin {"on" if flag else "off"} message #{message_id}'
        )
        return result

    @staticmethod
    def remove_message(message_id: int, chat_id: int) -> bool:
        if not DBWorker.__does_message_exist(message_id, chat_id):
            Logger.error(f'Failed to remove message #{message_id}: message not found')
            return False
        result = execute_query(
            f'update message_history set is_deleted = True where message_id = {message_id} and chat_id = {chat_id}'
        )
        Logger.fork_log(
            result,
            f'Message #{message_id} marked as deleted successfully',
            f'Failed to mark message #{message_id} as deleted'
        )
        return True

    @staticmethod
    def get_lot(lot_id: int) -> Optional[LotData]:
        try:
            lot_data = execute_query_with_cursor(
                f'select * from lot where lot_id = {lot_id}'
            )[0]
            result = DBWorker.__lot_data_from_tuple(lot_data)
            assert result is not None
            return result
        except Exception as e:
            Logger.error(f'Lot #{lot_id} not found:\n\t\t\t{e}')
            return None

    @staticmethod
    def get_saved_nls_params(user_id: int) -> Optional[LotData]:
        try:
            session_id = DBWorker.__get_session_for_user(user_id)
            assert session_id is not None
            data = execute_query_with_cursor(f'select * from new_lot_session where session_id = {session_id}')[0]
            for e in data:
                assert e is not None
            result = DBWorker.__get_lot_data_from_nls(data, user_id)
            assert result is not None
            return result
        except Exception as e:
            Logger.error(f'Failed to create new lot for user #{user_id}:\n\t\t\t{e}')
            return None

    @staticmethod
    def update_new_lot_session_params(user_id: int, param: NewLotSessionParam, value) -> bool:
        try:
            session_id = DBWorker.__get_session_for_user(user_id)
            assert session_id is not None
            is_text_value = param not in [NewLotSessionParam.price, NewLotSessionParam.lvl]
            value_token = str(value) if param not in [NewLotSessionParam.race, NewLotSessionParam.server] else \
                value.name
            quoted_value_token = f'\'{value_token}\'' if is_text_value else str(value_token)
            token = f'{param.name} = {quoted_value_token}'
            assert execute_query(f'update new_lot_session set {token} where session_id = {session_id}')
            return True
        except Exception as e:
            Logger.error(f'Failed to update params of new lot session for user #{user_id}:\n\t\t\t{e}')
            return False

    @staticmethod
    def get_filtered_lots(user_id: int) -> [LotData]:
        try:
            session_id = DBWorker.__get_session_for_user(user_id)
            assert session_id is not None
            data = execute_query_with_cursor(f'select * from search_session '
                                             f'where session_id = {session_id}')[0]
            server, race = data[1], data[2]
            min_lvl, max_lvl = data[3], data[4]
            min_price, max_price = data[5], data[6]
            data = [
                e for e in DBWorker.get_all_active_lots()
                if e.char.server.name == server and e.char.race.name == race
            ]
            lvl_filtered = [
                e for e in data
                if (min_lvl is None or min_lvl <= e.char.lvl) and (max_lvl is None or max_lvl >= e.char.lvl)
            ]
            price_filtered = [
                e for e in lvl_filtered
                if (min_price is None or min_price <= e.price) and (max_price is None or max_price >= e.price)
            ]
            return price_filtered
        except Exception as e:
            Logger.error(f'Failed to get filtered lots:\n\t\t\t{e}')
            return None

    @staticmethod
    def update_search_session_params(user_id: int, param: SearchSessionParam, value_token: str) -> bool:
        try:
            session_id = DBWorker.__get_session_for_user(user_id)
            assert session_id is not None
            assert execute_query(
                f'update search_session set {param.name} = {value_token} where session_id = {session_id}'
            )
            return True
        except AssertionError:
            Logger.error(f'Assertion error has occurred during updating search params for user #{user_id}')
        except Exception as e:
            Logger.error(f'Failed to update search params for user #{user_id}:\n\t\t\t{e}')
            return False

    @staticmethod
    def register_session(user: UserData) -> bool:
        if DBWorker.is_session_registered(user.user_id):
            return True
        try:
            DBWorker.insert_user(user)
            assert execute_query(f'insert into session values (null, {user.user_id}, {time.time()})')
            session_id = DBWorker.__get_session_for_user(user.user_id)
            assert session_id is not None
            assert DBWorker.__new_ss(session_id)
            assert DBWorker.__new_nls(session_id)
            return True
        except Exception as e:
            Logger.error(f'Assertion error has occurred during creating session for user #{user.user_id}')
            Logger.error(f'Failed to create session for user #{user.user_id}:\n\t\t\t{e}')
            return False

    @staticmethod
    def is_session_registered(user_id: int) -> bool:
        return len(execute_query_with_cursor(f'select * from session where user_id = {user_id}')) > 0

    @staticmethod
    def wipe_sessions() -> bool:
        try:
            result = True
            for session_id in execute_query_with_cursor(f'select * from session'):
                result = result and DBWorker.__remove_session(int(session_id[0]))
            assert result
            return True
        except Exception as e:
            Logger.error(f'Failed to wipe sessions:\n\t\t\t{e}')
            return False

    @staticmethod
    def is_user_registered(user_id: int) -> bool:
        return len(execute_query_with_cursor(f'select * from user where user_id = {user_id}')) > 0

    @staticmethod
    def insert_user(user: UserData) -> bool:
        if DBWorker.__find_user(user) is not None:
            return True
        result = execute_query(f'insert into user values ('
                               f'{user.user_id}, '
                               f'\'{user.username}\', '
                               f'\'{user.full_name}\''
                               f')')
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
    def close_lot(lot_id: int) -> bool:
        try:
            return execute_query(f'update lot set date_close = {time.time()} where lot_id = {lot_id}')
        except Exception as e:
            Logger.error(f'Failed to close lot #{lot_id}:\n\t\t\t{e}')
            return False

    @staticmethod
    def get_user_lots(user_id: int):
        return [converted for converted in [DBWorker.__lot_data_from_tuple(e) for e in
                                            execute_query_with_cursor(
                                                f'select * from lot where user_id = {user_id} and '
                                                f'date_close is null'
                                            )] if converted is not None]

    @staticmethod
    def __get_session_for_user(user_id: int) -> Optional[int]:
        if not DBWorker.is_user_registered(user_id) or not DBWorker.is_session_registered(user_id):
            return None
        try:
            return int(execute_query_with_cursor(f'select * from session where user_id = {user_id}')[0][0])
        except Exception:
            return None

    @staticmethod
    def __remove_session(session_id: int) -> bool:
        ss = execute_query(f'delete from search_session where session_id = {session_id}')
        nls = execute_query(f'delete from new_lot_session where session_id = {session_id}')
        s = execute_query(f'delete from session where session_id = {session_id}')
        return ss and nls and s

    @staticmethod
    def __new_ss(session_id: int) -> bool:
        return execute_query(
            f'insert into search_session values ({session_id}, null, null, null, null, null, null)'
        )

    @staticmethod
    def __new_nls(session_id: int) -> bool:
        return execute_query(
            f'insert into new_lot_session values ({session_id}, null, null, null, null, null, null, null, null, null)'
        )

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
                f'char_class = \'{char.char_class}\' and '
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
                user_id=data[0],
                username=data[1],
                full_name=data[2]
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
    def __get_lot_data_from_nls(data, user_id: int) -> Optional[LotData]:
        try:
            user_tuple = execute_query_with_cursor(
                f'select * from user where user_id = {user_id}'
            )[0]
            return LotData(
                char=CharData(
                    server=Server[data[1]],
                    race=Race[data[2]],
                    lvl=data[3],
                    char_class=data[4],
                    description=data[5],
                    heavens=data[6],
                    doll=data[7]
                ),
                user=DBWorker.__user_data_from_tuple(user_tuple),
                price=data[8],
                contact_info=data[9],
                date_opened=datetime.datetime.fromtimestamp(time.time())
            )
        except Exception as e:
            Logger.error(f'Failed to get lot data from saved params:\n\t\t\t{e}')
            return None

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

    @staticmethod
    def __does_message_exist(message_id: int, chat_id: int) -> bool:
        return len(execute_query_with_cursor(
            f'select * from message_history where message_id = {message_id} and chat_id = {chat_id}'
        )) > 0

    @staticmethod
    def __lot_visit_data_from_tuple(data):
        lot = DBWorker.get_lot(data[1])
        return LotVisitData(lot=lot, visit_date=datetime.date.fromtimestamp(data[2]))
