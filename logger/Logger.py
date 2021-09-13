import logging
import os
from threading import current_thread

from logger.LogLevel import LogLevel


class Logger:
    __logger = None
    __console_level = LogLevel.info
    __size_limit = 1048576

    @staticmethod
    def fork_log(log_level: LogLevel, cond: bool, text_true: str, text_false: str) -> None:
        message = text_true if cond else text_false
        if log_level == LogLevel.debug:
            Logger.debug(message)
        elif log_level == LogLevel.error:
            Logger.error(message)
        elif log_level == LogLevel.info:
            Logger.info(message)

    @staticmethod
    def error(message: str) -> None:
        Logger.__get_logger().error(message)
        if Logger.__console_level.value <= LogLevel.error.value:
            print(f'[{current_thread().name}] \033[31m{message}\033[0m')

    @staticmethod
    def info(message: str) -> None:
        Logger.__get_logger().info(message)
        if Logger.__console_level.value <= LogLevel.info.value:
            print(f'[{current_thread().name}] \033[34m{message}\033[0m')

    @staticmethod
    def debug(message: str) -> None:
        Logger.__get_logger().debug(message)
        if Logger.__console_level.value <= LogLevel.debug.value:
            print(f'[{current_thread().name}] \033[32m{message}\033[0m')

    @staticmethod
    def set_console_log_level(level: LogLevel) -> None:
        Logger.__console_level = level

    @staticmethod
    def __get_logger() -> logging.Logger:
        if not Logger.__logger:
            return Logger.__init_logger()
        return Logger.__logger

    @staticmethod
    def __init_logger() -> logging.Logger:
        logger = logging.getLogger('root')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(f'%(asctime)s [%(levelname)s][{current_thread().name}]:\t %(message)s')
        fh = logging.FileHandler(Logger.get_log_file())
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        Logger.__logger = logger
        return logger

    @staticmethod
    def get_log_file() -> str:
        if not os.path.isdir('logs'):
            os.mkdir('logs')
        logs = [e for e in os.listdir('logs')
                if len(e.split('log_')) > 1 and len(e.split('log_')[1].split('.log')) > 1 and
                e.split('log_')[1].split('.log')[0].isnumeric()]
        if not len(logs):
            return Logger.__new_log_file(0)

        last_index = max([int(e.split('log_')[1].split('.log')[0]) for e in logs])
        last = [e for e in logs if len(e.split(str(last_index))) > 1][0]
        size = os.path.getsize(f'logs/{last}')
        if size > Logger.__size_limit:
            return Logger.__new_log_file(last_index + 1)
        return f'logs/{last}'

    @staticmethod
    def __new_log_file(index: int) -> str:
        open(f'logs/log_{index}.log', 'w+').close()
        return f'logs/log_{index}.log'


