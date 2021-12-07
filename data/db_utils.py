import sqlite3
from sqlite3 import Cursor

from logger.Logger import Logger

__conn = sqlite3.connect('pwstore.db', check_same_thread=False)


def init_db(load_test_data: bool = True) -> None:
    cursor = get_cursor()
    with open('data/db_gen.sql', 'r') as file:
        Logger.debug('Initializing tables...')
        cursor.executescript(file.read())
        Logger.debug('Tables has been created')
    if load_test_data:
        with open('data/data_sample.sql') as file:
            Logger.debug('Loading sample data...')
            cursor.executescript(file.read())
            Logger.debug('Sample data has been loaded')
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
    names = __get_names_of_all_tables()
    return __perform_operations_on_table(
        names,
        'delete from {0} where true',
        '{0} has been cleaned successfully',
        'Failed to clean {0}'
    )


def drop_db() -> bool:
    names = __get_names_of_all_tables()
    return __perform_operations_on_table(
        names,
        'drop table {0}',
        '{0} has been dropped successfully',
        'Failed to drop {0}'
    )


def __perform_operations_on_table(tables: [str], query: str, success_mes: str, fail_mes: str) -> bool:
    result = True
    for table in tables:
        success = execute_query(query.format(table))
        if success:
            Logger.debug(success_mes.format(table))
        else:
            Logger.error(fail_mes.format(table))
        result &= success
    if result:
        Logger.debug(success_mes.format(('all the tables',)))
    else:
        Logger.debug(fail_mes.format(('all the tables',)))
    return result


def __get_names_of_all_tables() -> [str]:
    with open('data/db_gen.sql') as file:
        lines = file.read().split('\n')
    names = [line.split('table ')[-1] for line in lines if len(line.split('create table')) > 1]
    return names
