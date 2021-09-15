from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.utils.bot_utils import send_greeting
from bot.utils.cb_utils import send
from bot.utils.ui_constr import get_remove_confirm_kb, get_return_kb
from controllers.DBController import DBController
from entity.enums.Event import Event


def close_lot_cb(call: CallbackQuery, value, bot: TeleBot):
    lot_id = int(value.split('_')[1])
    send(
        bot, call.from_user.id,
        Event.close_lot_confirm,
        None,
        get_remove_confirm_kb('close_conf', lot_id)
    )


def close_conf_cb(call: CallbackQuery, value, bot: TeleBot):
    lot_id = int(value.split('_')[1])
    option = value.split('_')[0]
    if option == 'yes':
        DBController.close_lot(lot_id)
        send(
            bot,
            call.from_user.id,
            Event.close_lot_success,
            None,
            get_return_kb()
        )
    else:
        send_greeting(bot, call.from_user.id)

