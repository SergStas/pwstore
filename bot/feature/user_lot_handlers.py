from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.utils.cb_utils import lots_list_default_handler, send_default_page
from bot.utils.ui_constr import get_remove_button
from controllers.DBController import DBController


def user_lots_cb(call: CallbackQuery, value: str, bot: TeleBot):
    lots_list_default_handler(
        bot,
        call,
        value,
        lambda l_bot, l_call, l_page: send_default_page(
            l_bot,
            l_page,
            DBController.get_user_lots(l_call.from_user.id),
            l_call.from_user.id,
            'user_lots'
        ),
        lambda lot: get_remove_button('close', lot.lot_id)
    )
