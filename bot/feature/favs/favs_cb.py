from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.utils.CallbackKeyEncoder import *
from bot.utils.cb_utils import lots_list_default_handler, send_default_page, send
from bot.utils.markup_factories import get_lots_list_default_markup_factory
from bot.utils.ui_constr import get_return_kb
from controllers.DBController import DBController
from entity.enums.Event import Event


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
    favs = DBController.get_favs(call.from_user.id)
    if len(favs) == 0:
        send(bot, call.from_user.id, Event.no_favs, markup=get_return_kb())
        return
    lots_list_default_handler(
        bot=bot,
        value=value,
        call=call,
        page_switcher=lambda l_bot, l_call, l_page: send_default_page(
            bot=l_bot,
            page=l_page,
            lots=favs,
            user_id=l_call.from_user.id,
            key=cb_key,
            title_event=Event.found_favs,
        ),
        markup_factory=get_lots_list_default_markup_factory(cb_key, call)
    )
