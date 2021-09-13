import sqlite3
from sqlite3 import Cursor

from logger.Logger import Logger

__conn = sqlite3.connect('pwstore.db', check_same_thread=False)


def init_db() -> None:
    with open('data/db_gen.sql', 'r') as file:
        cursor = get_cursor()
        cursor.executescript(file.read())
        __conn.commit()
    Logger.debug(f'DB has been inited')


def get_cursor() -> Cursor:
    return __conn.cursor()


def execute_query(query: str) -> bool:
    try:
        get_cursor().execute(query)
        __conn.commit()
        return True
    except Exception as e:
        Logger.error(f'An error has occurred during executing query:\n\t\tquery: {query}\n\t\terror: {e}')
        return False


def execute_query_with_cursor(query: str) -> list:
    try:
        cursor = get_cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        Logger.error(f'An error has occurred during executing query:\n\t\tquery: {query}\n\t\terror: {e}')
        return []


def cleanup_db() -> bool:
    result = execute_query('delete from user where true') and \
           execute_query('delete from character where true') and \
           execute_query('delete from lot where true')
    Logger.debug(f'DB has been cleaned')
    return result


def drop_db() -> bool:
    names = __get_names_of_all_tables()
    result = True
    for table in names:
        success = execute_query(f'drop table {table}')
        if success:
            Logger.debug(f'Table {table} has been dropped')
        else:
            Logger.error(f'Failed to drop table {table}')
        result &= success
    # result = execute_query('drop table character') and \
    #          execute_query('drop table user') and \
    #          execute_query('drop table lot') and \
    #          execute_query('drop table session') and \
    #          execute_query('drop table search_session') and \
    #          execute_query('drop table new_lot_session')
    if result:
        Logger.debug(f'DB has been dropped successfully')
    else:
        Logger.debug(f'DB wasn\'t dropped completely')
    return result


def __get_names_of_all_tables() -> [str]:
    with open('data/db_gen.sql') as file:
        lines = file.read().split('\n')
    names = [line.split('table ')[-1] for line in lines if len(line.split('create table')) > 1]
    return names
    # return [e[0] for e in execute_query_with_cursor(
    #     'select name from sqlite_master where type = \'table\''
    # )]
