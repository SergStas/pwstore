from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.utils.CallbackKeyEncoder import *
from bot.utils.cb_utils import lots_list_default_handler, send_default_page
from bot.utils.markup_factories import get_lots_list_default_markup_factory
from controllers.DBController import DBController


def favs_cb(call: CallbackQuery, value, bot: TeleBot):
    if __check_and_process_adding(str(value), call) or \
            __check_and_process_removing(str(value), call):
        return
    __favs_list_cb(call=call, value=value, bot=bot)


def __check_and_process_adding(value: str, call: CallbackQuery) -> bool:
    if len(value.split('add')) > 1:
        lot_id = int(value.split('_')[1])
        DBController.add_to_favs(user_id=call.from_user.id, lot_id=lot_id)
        return True
    return False


def __check_and_process_removing(value: str, call: CallbackQuery) -> bool:
    if len(value.split('remove')) > 1:
        lot_id = int(value.split('_')[1])
        DBController.remove_from_favs(user_id=call.from_user.id, lot_id=lot_id)
        return True
    return False


def __favs_list_cb(call: CallbackQuery, value: str, bot: TeleBot, cb_key: str = 'favs'):
    lots_list_default_handler(
        bot=bot,
        value=value,
        call=call,
        page_switcher=lambda l_bot, l_call, l_page: send_default_page(
            bot=l_bot,
            page=l_page,
            lots=DBController.get_favs(l_call.from_user.id),
            user_id=l_call.from_user.id,
            key=cb_key
        ),
        markup_factory=get_lots_list_default_markup_factory(cb_key, call)
    )
