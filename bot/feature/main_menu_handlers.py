from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.spell.SpellHandler import SpellHandler
from bot.utils.ui_constr import get_server_selector_kb, get_sell_menu_kb
from entity.enums.Event import Event


def main_menu_cb(call: CallbackQuery, value: str, bot: TeleBot):
    bot.delete_message(call.from_user.id, call.message.message_id)
    if value == 'buy':
        show_buy_menu(bot, call.from_user.id)
    elif value == 'sell':
        show_sell_menu(bot, call.from_user.id)


def show_buy_menu(bot: TeleBot, user_id: int):
    bot.send_message(
        chat_id=user_id,
        text=SpellHandler.get_message(Event.search_select_server),
        reply_markup=get_server_selector_kb('search_server')
    )


def show_sell_menu(bot: TeleBot, user_id: int):
    bot.send_message(
        chat_id=user_id,
        text=SpellHandler.get_message(Event.sell_menu),
        reply_markup=get_sell_menu_kb('sell_menu')
    )
