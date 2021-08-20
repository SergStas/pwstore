from telebot.types import Message, CallbackQuery

from bot.feature.close_lot_handlers import close_lot_cb, close_conf_cb
from bot.feature.new_lot_handlers import new_lot_race_cb, new_lot_server_cb
from bot.feature.search_lot_handlers import search_server_cb, search_race_cb
from bot.feature.search_results_handlers import all_lots_cb
from bot.feature.sell_menu_handlers import sell_menu_cb
from bot.feature.user_lot_handlers import user_lots_cb
from bot.spell.SpellHandler import SpellHandler
from bot.utils.bot_utils import init_bot, check_user_session
from bot.utils.cb_utils import send
from bot.utils.ui_constr import dec_cb_data, get_server_selector_kb, get_sell_menu_kb
from entity.dataclass.UserData import UserData
from entity.enums.Event import Event
from logger.LogLevel import LogLevel
from logger.Logger import Logger

Logger.set_console_log_level(LogLevel.debug)
__bot = init_bot()


@__bot.message_handler(commands=['start'])
def handle_greeting(message: Message):
    __check_mes(message)
    send(__bot, message.from_user.id, Event.first_launch)


@__bot.message_handler(commands=['help'])
def show_help(message: Message):
    __check_mes(message)
    send(__bot, message.from_user.id, Event.help)


@__bot.message_handler(commands=['sell'])
def handle_sell_menu(message: Message):
    __check_mes(message)
    __bot.send_message(
        chat_id=message.from_user.id,
        text=SpellHandler.get_message(Event.sell_menu),
        reply_markup=get_sell_menu_kb('sell_menu')
    )


@__bot.message_handler(commands=['buy'])
def handle_buy_menu(message: Message):
    __check_mes(message)
    __bot.send_message(
        chat_id=message.from_user.id,
        text=SpellHandler.get_message(Event.search_select_server),
        reply_markup=get_server_selector_kb('search_server')
    )


@__bot.message_handler(content_types=['text'])
def handle_other(message: Message):
    __check_mes(message, True)
    send(__bot, message.from_user.id, Event.unknown_command, (message.text,))


@__bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    key, value = dec_cb_data(call.data)
    key_dict = {
        'search_server': search_server_cb,
        'search_race': search_race_cb,
        'sell_menu': sell_menu_cb,
        'new_lot_server': new_lot_server_cb,
        'new_lot_race': new_lot_race_cb,
        'show_lots': all_lots_cb,
        'user_lots': user_lots_cb,
        'close': close_lot_cb,
        'close_conf': close_conf_cb
    }
    key_dict[key](call, value, __bot)


def __check_mes(message: Message, show_greeting=False):
    user = UserData(message.from_user.id, message.from_user.username, message.from_user.full_name)
    if not check_user_session(user):
        if show_greeting:
            handle_greeting(message)
    Logger.debug(f'User {message.from_user.id} has sent message: {message.text}')


def start_bot():
    Logger.debug('Bot polling has started')
    __bot.polling(none_stop=True)
