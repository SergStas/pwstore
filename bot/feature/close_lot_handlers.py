from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.spell.SpellHandler import SpellHandler
from bot.utils.cb_utils import send
from bot.utils.ui_constr import get_remove_confirm_kb
from controllers.DBController import DBController
from entity.enums.Event import Event


def close_lot_cb(call: CallbackQuery, value, bot: TeleBot):
    lot_id = int(value.split('_')[1])
    bot.delete_message(call.from_user.id, call.message.id)
    bot.send_message(
        call.from_user.id,
        SpellHandler.get_message(Event.close_lot_confirm),
        reply_markup=get_remove_confirm_kb('close_conf', lot_id)
    )


def close_conf_cb(call: CallbackQuery, value, bot: TeleBot):
    lot_id = int(value.split('_')[1])
    option = value.split('_')[0]
    bot.delete_message(call.from_user.id, call.message.id)
    if option == 'yes':
        DBController.close_lot(lot_id)
        send(bot, call.from_user.id, Event.close_lot_success)
