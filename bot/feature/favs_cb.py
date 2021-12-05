from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.feature.search_results_handlers import all_lots_cb
from bot.utils.cb_utils import lots_list_default_handler, send_default_page
from bot.utils.ui_constr import get_all_lots_markup_kb
from controllers.DBController import DBController


def favs_cb(call: CallbackQuery, value, bot: TeleBot):
    if __check_and_process_adding(str(value), call, bot) or \
            __check_and_process_removing(str(value), call, bot):
        return

    lots_list_default_handler(
        bot=bot,
        value=value,
        call=call,
        page_switcher=lambda l_bot, l_call, l_page: send_default_page(
            bot=l_bot,
            page=l_page,
            lots=DBController.get_favs(l_call.from_user.id),
            user_id=l_call.from_user.id,
            key='favs'
        ),
        markup_factory=lambda l_lot: get_all_lots_markup_kb(
            cb_key='favs',
            lot=l_lot,
            is_fav=DBController.is_fav(lot_id=l_lot.lot_id, user_id=call.from_user.id),
            page=0,
        ),
    )


def __check_and_process_adding(value: str, call: CallbackQuery, bot: TeleBot) -> bool:
    if len(value.split('add')) > 1:
        lot_id = int(value.split('_')[1])
        DBController.add_to_favs(user_id=call.from_user.id, lot_id=lot_id)
        all_lots_cb(call=call, value=str(lot_id), bot=bot)
        return True
    return False


def __check_and_process_removing(value: str, call: CallbackQuery, bot: TeleBot) -> bool:
    if len(value.split('remove')) > 1:
        lot_id = int(value.split('_')[1])
        DBController.remove_from_favs(user_id=call.from_user.id, lot_id=lot_id)
        all_lots_cb(call=call, value=str(lot_id), bot=bot, cb_key='favs')
        return True
    return False
