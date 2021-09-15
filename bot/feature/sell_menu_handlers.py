from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.utils.cb_utils import send, send_default_page
from bot.utils.ui_constr import get_server_selector_kb, get_return_kb
from controllers.DBController import DBController
from entity.enums.Event import Event
from entity.enums.SellMenuOption import SellMenuOption


def sell_menu_cb(call: CallbackQuery, value: str, bot: TeleBot):
    option = SellMenuOption[value]
    if option == SellMenuOption.new_lot:
        send(
            bot,
            call.from_user.id,
            Event.new_lot_input_server,
            None,
            get_server_selector_kb('new_lot_server')
        )
    elif option == SellMenuOption.show_lots:
        user_lots = DBController.get_user_lots(call.from_user.id)
        if len(user_lots) == 0:
            send(
                bot,
                call.from_user.id,
                Event.no_user_lots_found,
                None,
                get_return_kb()
            )
        else:
            send_default_page(bot, 0, user_lots, call.from_user.id, 'user_lots')
