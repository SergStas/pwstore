from telebot.types import Message

from bot.SpellHandler import SpellHandler
from bot.bot_utils import init_bot, check_user_session
from entity.enums.SpellEvent import SpellEvent
from logger.LogLevel import LogLevel
from logger.Logger import Logger

Logger.set_console_log_level(LogLevel.debug)
__bot = init_bot()


@__bot.message_handler(commands=['start'])
def handle_greeting(message: Message):
    __log_mes(message)
    __bot.send_message(message.from_user.id, __sp(SpellEvent.first_launch))
    if not check_user_session(message.from_user.id):
        show_help(message)


@__bot.message_handler(commands=['help'])
def show_help(message: Message):
    __log_mes(message)
    __bot.send_message(message.from_user.id, __sp(SpellEvent.help))


@__bot.message_handler(commands=['sell'])
def handle_sell_menu(message: Message):
    __log_mes(message)
    __bot.send_message(message.from_user.id, 'select server')  # TODO


@__bot.message_handler(commands=['buy'])
def handle_buy_menu(message: Message):
    __log_mes(message)
    __bot.send_message(message.from_user.id, 'choose action')  # TODO


@__bot.message_handler(content_types=['text'])
def handle_other(message: Message):
    __log_mes(message)
    if not check_user_session(message.from_user.id):  # delete condition block after debug
        handle_greeting(message)
        show_help(message)
    __bot.send_message(message.from_user.id, __sp(SpellEvent.unknown_command, (message.text,)))


def __sp(event: SpellEvent, args=None) -> str:
    return SpellHandler.get_message(event, args)


def __log_mes(message: Message):
    Logger.debug(f'User {message.from_user.id} has sent message: {message.text}')


def start_bot():
    Logger.debug('Bot polling has started')
    __bot.polling(none_stop=True)
