from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from bot.feature.close_lot_handlers import close_lot_cb, close_conf_cb
from bot.feature.favs.favs_cb import favs_cb
from bot.feature.main_menu_handlers import show_buy_menu, main_menu_cb, show_sell_menu
from bot.feature.new_lot_handlers import new_lot_race_cb, new_lot_server_cb
from bot.feature.lotvisit.LotVisitCallback import LotVisitCallback
from bot.feature.search_lot_handlers import search_server_cb, search_race_cb
from bot.feature.search_results_handlers import all_lots_cb
from bot.feature.sell_menu_handlers import sell_menu_cb
from bot.feature.sellerlots.SellerLotsCallback import *
from bot.feature.user_lot_handlers import user_lots_cb
from bot.utils.CallbackKeyEncoder import CallbackKeyEncoder
from bot.utils.bot_utils import init_bot, check_message, greeting, send_greeting
from bot.utils.cb_utils import send
from bot.utils.ui_constr import get_return_kb
from entity.enums.Event import Event
from logger.LogLevel import LogLevel
from logger.Logger import Logger

Logger.set_console_log_level(LogLevel.debug)
__bot = init_bot()

prev_command: str


@__bot.message_handler(commands=['start'])
def handle_greeting(message: Message):
    greeting(__bot, message)


@__bot.message_handler(commands=['help'])
def show_help(message: Message):
    check_message(__bot, message)
    send(__bot, message.from_user.id, Event.help, None, get_return_kb())


@__bot.message_handler(commands=['sell'])
def handle_sell_menu(message: Message):
    check_message(__bot, message)
    show_sell_menu(__bot, message.from_user.id)


@__bot.message_handler(commands=['buy'])
def handle_buy_menu(message: Message):
    check_message(__bot, message)
    show_buy_menu(__bot, message.from_user.id)


@__bot.message_handler(content_types=['text'])
def handle_other(message: Message):
    check_message(__bot, message, True)
    send(__bot, message.from_user.id, Event.unknown_command, (message.text,), get_return_kb())


@__bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    global prev_command
    key, value = CallbackKeyEncoder.dec_cb_data(call.data)
    f_key = key
    if key == 'void':
        key, value = CallbackKeyEncoder.decode_void(call.data)
    Logger.info(call.data.upper())
    key_dict = {
        'search_server': search_server_cb,
        'search_race': search_race_cb,
        'sell_menu': sell_menu_cb,
        'new_lot_server': new_lot_server_cb,
        'new_lot_race': new_lot_race_cb,
        'show_lots': all_lots_cb,
        'user_lots': user_lots_cb,
        'close': close_lot_cb,
        'close_conf': close_conf_cb,
        'main_menu': main_menu_cb,
        'back_to_mm': __handle_back_to_mm,
        'favs': favs_cb,
        'seller_lots': SellerLotsCallback.execute,
        'lot_visit': LotVisitCallback.execute,
    }
    key_dict[key](call, value, __bot)
    if f_key == 'void':
        Logger.info('PREV:' + prev_command.upper())
        prev_key, prev_value = CallbackKeyEncoder.dec_cb_data(prev_command)
        key_dict[prev_key](call, prev_value, __bot)
    else:
        prev_command = call.data


def __handle_back_to_mm(call: CallbackQuery, value: str, bot: TeleBot):
    bot.clear_step_handler_by_chat_id(call.from_user.id)
    send_greeting(__bot, call.from_user.id)


def start_bot(loop_forever: bool):
    Logger.debug('Bot polling has started')
    if loop_forever:
        while True:
            try:
                __bot.polling(none_stop=True)
            except Exception as e:
                Logger.error(
                    f'FATAL ERROR:\n\t\t\t{e}'
                )
    else: __bot.polling(none_stop=True)
