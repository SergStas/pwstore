import sqlite3
from sqlite3 import Cursor

__conn = sqlite3.connect('pwstore.db', check_same_thread=False)


def init_db() -> None:
    with open('data/db_gen.sql', 'r') as file:
        cursor = get_cursor()
        cursor.executescript(file.read())
        __conn.commit()


def get_cursor() -> Cursor:
    return __conn.cursor()


def execute_query(query: str) -> bool:
    try:
        get_cursor().execute(query)
        __conn.commit()
        return True
    except Exception as e:
        return False


def execute_query_with_cursor(query: str) -> list:
    try:
        cursor = get_cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except Exception:
        return []


def cleanup_db() -> bool:
    result = execute_query('delete from user where true') and \
           execute_query('delete from character where true') and \
           execute_query('delete from lot where true')
    return result


def drop_db() -> bool:
    result = execute_query('drop table character') and \
           execute_query('drop table user') and \
           execute_query('drop table lot')
    return result
