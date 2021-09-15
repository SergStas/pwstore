import os

from telebot import TeleBot
from telebot.types import Message, User

from bot.utils.cb_utils import send
from bot.utils.ui_constr import get_main_menu_kb
from entity.dataclass.UserData import UserData
from entity.enums.Event import Event
from logger.Logger import Logger
from controllers.DBController import DBController


def init_bot() -> TeleBot:
    token = get_token()
    Logger.debug('Starting bot...')
    res_bot = TeleBot(token)
    Logger.debug('Bot has been inited')
    DBController.wipe_sessions()
    return res_bot


def greeting(bot: TeleBot, message: Message):
    check_message(bot, message)
    send_greeting(bot, message.from_user.id)


def check_message(bot: TeleBot, message: Message, show_greeting=False):
    DBController.save_message(message.message_id, message.chat.id)
    if not check_user_session(userdata_from_user(message.from_user)):
        if show_greeting:
            greeting(bot, message)
    Logger.debug(f'User #{message.from_user.id} has sent message: {message.text}')


def userdata_from_user(user: User) -> UserData:
    return UserData(user.id, user.username, user.full_name)


def check_user_session(user: UserData) -> bool:
    DBController.register_session(user)
    return False


def get_token() -> str:
    if not os.path.isfile('security.txt'):
        Logger.error('Access file not found')
        raise PermissionError('File \'security.txt\' with bot token not found')
    with open('security.txt', 'r') as file:
        return [e.split('=')[1] for e in file.read().split('\n')
                if e != '' and len(e.split('bot_token')) > 1][0]


def send_greeting(bot: TeleBot, user_id: int):
    send(
        bot,
        user_id,
        Event.first_launch,
        None,
        get_main_menu_kb('main_menu')
    )
