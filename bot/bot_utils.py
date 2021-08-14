import os

import telebot

from data.DBWorker import DBWorker
from logger.Logger import Logger


def start_bot() -> telebot.TeleBot:
    token = get_token()
    Logger.debug('Starting bot...')
    res_bot = telebot.TeleBot(token)
    Logger.debug('Bot has been started')
    DBWorker.wipe_sessions()
    return res_bot


def check_user_session(user_id: int) -> bool:
    if DBWorker.is_session_registered(user_id):
        return True
    DBWorker.register_session(user_id)
    return False


def get_token() -> str:
    if not os.path.isfile('security.txt'):
        Logger.error('Access file not found')
        raise PermissionError('File \'security.txt\' with bot token not found')
    with open('security.txt', 'r') as file:
        return [e.split('=')[1] for e in file.read().split('\n')
                if e != '' and len(e.split('bot_token')) > 1][0]
