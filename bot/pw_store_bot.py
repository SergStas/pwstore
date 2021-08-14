import telebot
from telebot.types import Message

from bot.SpellHandler import SpellHandler
from bot.bot_utils import start_bot, check_user_session, get_token
from entity.dataclass.UserData import UserData
from entity.enums.SpellEvent import SpellEvent
from logger.Logger import Logger


__bot = start_bot()
# __bot = telebot.TeleBot(get_token())
# Logger.debug('Bot has been started')


def init():
    Logger.debug('Starting...')


@__bot.message_handler(commands=[
    'find_account',
    'sell_account',
    'help'
])
def handle_start_page(message: Message):
    commands_handler = {
        '/find_account': __select_server,
        '/sell_account': __choose_open_or_close_action,
        '/help': __show_help
    }

    __handle_greeting(message)

    text = message.text
    if text in commands_handler.keys():
        action = commands_handler[text]
        __bot.register_next_step_handler(message, action)
    else:
        __bot.send_message(message.from_user.id, __sp(SpellEvent.unknown_command, (message.text,)))


def __handle_greeting(message: Message):
    if not check_user_session(message.from_user.id):
        __bot.send_message(message.from_user.id, __sp(SpellEvent.first_launch))
        __show_help(message)


def __show_help(message: Message):
    __bot.send_message(message.from_user.id, __sp(SpellEvent.help))


def __select_server(message: Message):
    __bot.send_message(message.from_user.id, 'select server')  # TODO


def __choose_open_or_close_action(message: Message):
    __bot.send_message(message.from_user.id, 'choose action')  # TODO


def __sp(event: SpellEvent, args=None) -> str:
    return SpellHandler.get_message(event, args)


__bot.polling(none_stop=True)  # FIXME
