import os

import telebot

from logger.Logger import Logger
from controllers.DBController import DBController


def init_bot() -> telebot.TeleBot:
    token = get_token()
    Logger.debug('Starting bot...')
    res_bot = telebot.TeleBot(token)
    Logger.debug('Bot has been inited')
    DBController.wipe_sessions()
    return res_bot


def check_user_session(user_id: int) -> bool:
    DBController.register_session(user_id)
    return False


def get_token() -> str:
    if not os.path.isfile('security.txt'):
        Logger.error('Access file not found')
        raise PermissionError('File \'security.txt\' with bot token not found')
    with open('security.txt', 'r') as file:
        return [e.split('=')[1] for e in file.read().split('\n')
                if e != '' and len(e.split('bot_token')) > 1][0]
