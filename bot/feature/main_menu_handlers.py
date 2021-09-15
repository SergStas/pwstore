from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.utils.cb_utils import send
from bot.utils.ui_constr import get_server_selector_kb, get_sell_menu_kb
from entity.enums.Event import Event


def main_menu_cb(call: CallbackQuery, value: str, bot: TeleBot):
    if value == 'buy':
        show_buy_menu(bot, call.from_user.id)
    elif value == 'sell':
        show_sell_menu(bot, call.from_user.id)


def show_buy_menu(bot: TeleBot, user_id: int):
    send(
        bot,
        user_id,
        Event.search_select_server,
        None,
        get_server_selector_kb('search_server')
    )


def show_sell_menu(bot: TeleBot, user_id: int):
    send(
        bot,
        user_id,
        Event.sell_menu,
        None,
        get_sell_menu_kb('sell_menu')
    )
