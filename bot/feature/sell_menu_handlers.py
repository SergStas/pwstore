from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.spell.SpellHandler import SpellHandler
from bot.utils.cb_utils import send, send_default_page
from bot.utils.ui_constr import get_server_selector_kb
from controllers.DBController import DBController
from entity.enums.Event import Event
from entity.enums.SellMenuOption import SellMenuOption


def sell_menu_cb(call: CallbackQuery, value: str, bot: TeleBot):
    bot.delete_message(call.from_user.id, call.message.id)
    option = SellMenuOption[value]
    if option == SellMenuOption.new_lot:
        bot.send_message(
            chat_id=call.from_user.id,
            text=SpellHandler.get_message(Event.new_lot_input_server),
            reply_markup=get_server_selector_kb('new_lot_server')
        )
    elif option == SellMenuOption.show_lots:
        user_lots = DBController.get_user_lots(call.from_user.id)
        if len(user_lots) == 0:
            send(bot, call.from_user.id, Event.no_user_lots_found)
        else:
            send_default_page(bot, 0, user_lots, call.from_user.id, 'user_lots')
